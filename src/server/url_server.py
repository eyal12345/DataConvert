from src.client.url_process import URLProcess
from concurrent.futures import ThreadPoolExecutor
from collections import deque
import threading
import requests
import re

# seconds to wait for a connection and for each chunk of the response, so a
# server that never answers cannot freeze the export
TIMEOUT = (5, 10)
# maximum bytes to download from a single page, so a slow endless response
# cannot keep the export running forever
MAX_PAGE_BYTES = 5 * 1024 * 1024
# how many urls are downloaded at the same time instead of one after the other
MAX_WORKERS = 8
# how many urls may wait for their turn, keeps the memory of the downloads bounded
MAX_PENDING = MAX_WORKERS * 2
# status codes which constitute an approach to an url
ACCESS_CODES = [200, 301, 302, 303, 403, 406, 500, 999]

class URLServer(URLProcess):

    def __init__(self, frame, root: str, max_depth: int) -> None:
        """
        constructor for URL object
        attributes:
            root (str): the main url to be extracted all sub-urls up to max depth level
            max_depth (int): the depth level to be extracted sub-urls up to him
            format (str): the configuration data file for the item
            serial (int): the id number for a new url
            visited (set): cumulative group of urls that is checked
            local (local): the storage of the session which belongs to each thread
        """
        super().__init__(frame)
        self.root = root
        self.max_depth = max_depth
        self.serial = 0
        self.visited = set()
        self.local = threading.local()
        self.track = None

    def update_track_widgets(self):
        """
        display all messages during the progress
        """
        tracks = self.frame.winfo_children()[11:]
        self.track = {
            "status": {"depth": tracks[0], "quantity": tracks[1]},
            "progress": {"per_url": tracks[3], "per_depth": tracks[5]},
            "added": {"sub-url": tracks[6], "overall": tracks[8]},
            "so_far": {"update": tracks[7], "count": 1},
        }

    def get_session(self) -> requests.Session:
        """
        return the session of the running thread, a session keeps the connections to a
        host open instead of opening a new connection for each url of the same host
        returns:
            session (Session): the requests session which belongs to the running thread
        """
        session = getattr(self.local, 'session', None)
        if session is None:
            session = requests.Session()
            session.headers.update({'User-Agent': 'Mozilla/5.0'})
            self.local.session = session
        return session

    def run_in_parallel(self, action, items: list):
        """
        run an action on all the items with several threads at the same time, while the
        results are returned by the original order of the items
        parameters:
            action (callable): the action which is executed for each item
            items (list): the items which are handled
        yields:
            result (any): the result of the action for the next item by order
        """
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            pending = deque()
            for item in items:
                # hold a limited number of downloads at a time, the rest wait for their turn
                pending.append(pool.submit(action, item))
                if len(pending) >= MAX_PENDING:
                    yield pending.popleft().result()
            while pending:
                yield pending.popleft().result()

    def try_open_url(self, url: str) -> bool:
        """
        return if url is valid access
        parameters:
            url (str): an url which is checked if is valid
        returns:
            True or False (bool): if a status code constitutes an approach to url
        """
        try:
            # stream the answer, only the status code is needed and not the body
            with self.get_session().get(url, allow_redirects=False, timeout=TIMEOUT, stream=True) as access:
                return access.status_code in ACCESS_CODES
        except requests.exceptions.RequestException:
            return False

    def read_page_data(self, url: str) -> tuple[bool, str]:
        """
        download the html of an url up to a limited size together with his access, one
        request supplies both instead of asking the same url twice
        parameters:
            url (str): the url which his content is downloaded
        returns:
            access (bool): if a status code constitutes an approach to url
            html (str): the decoded content of the page, empty when there is no access
        """
        content = bytearray()
        try:
            with self.get_session().get(url, allow_redirects=False, timeout=TIMEOUT, stream=True) as response:
                access = response.status_code in ACCESS_CODES
                if access:
                    for chunk in response.iter_content(chunk_size=8192):
                        content += chunk
                        # stop reading a page that is too heavy instead of waiting for his end
                        if len(content) >= MAX_PAGE_BYTES:
                            break
            return access, content.decode('latin1')
        except requests.exceptions.RequestException:
            return False, ''

    def extract_data_childs(self, dataset: dict[str, any], html: str) -> list[dict]:
        """
        extract data sub-urls set from the content of the url in the dataset
        parameters:
            dataset (dict): data of sub-url which from him extract all sub-urls which is contains
            html (str): the already downloaded content of the url in the dataset
        returns:
            datasets (list): collection of sub-urls in same depth level from the main url
        """
        father, depth = dataset['child'], dataset['depth']
        datasets = []
        urls = re.findall(r'(?<=href=")[https:]*[/{1,2}#]*[\w+.\-/=?_#]*(?=")', html)
        if urls:
            self.track["added"]["sub-url"].config(text=f'waiting to new sources from this url')
            childs = self.fix_urls(father, urls)
            datasets = self.create_child_datasets(father, childs, depth + 1)
        return datasets

    def fix_urls(self, father: str, urls: list[str]) -> list[str]:
        """
        return fix list of sub-urls
        parameters:
            father (str): the url that connected to incomplete sub-urls
            urls (list): list of incomplete sub-urls which need to be fixed
        returns:
            fix_urls (list): list of the sub-urls after a fix
        """
        fix_urls = []
        for url in urls:
            if '?' in url:
                url = url[:url.find('?')]
            if '#' in url:
                url = url[:url.find('#')]
            if url.startswith('..'):
                url = father.rsplit('/', 1)[0] + url[url.find('/'):]
            elif url.startswith('//'):
                url = father.split('/')[0] + '' + url
            elif url.startswith('/') and len(url) > 1:
                url = father.split('/')[0] + '//' + father.split('/')[2] + url
            elif url.startswith('./'):
                url = father.split('/')[0] + '//' + father.split('/')[2] + '/' + url[2:]
            elif not '/' in url or re.match(r'^[a-zA-Z]+/', url) is not None:
                url = father.split('/')[0] + '//' + father.split('/')[2] + '/' + url
            url = url[:-1] if url.endswith('/') else url
            if url and not url in self.visited:
                fix_urls.append(url)
        return fix_urls

    def is_ignore_url(self, url: str) -> bool:
        """
        returns whether an url is relevant for display by extension of file
        parameters:
            url (str): the url which is checked if is reference to html page and not to file
        returns:
            True or False (bool): returns if an url is file with specific extensions
        """
        if bool(re.search(r"(?<=\.)(css|rss|js|jpg|json|png|pdf|php|xml|txt|svg|org|woff2|doc|io|ico|aspx|w2p|gz|zip|jsp[x|f]?)$", url)):
            return True
        return False

    def is_familiar_url(self, url: str) -> bool:
        """
        returns whether an url is visited under another path
        parameters:
            url (str): the url which is checked if is visited before
        returns:
            True or False (bool): returns if an url is under another path that is checked
        """
        if 'wikipedia' in url:
            org_val_search = self.search_url_part(r"(?<=/)[\-\.()\w\d]+$", self.root)
            cur_val_search = self.search_url_part(r"(?<=/)[\-\.()\w\d]+$", url)
            org_language = self.search_url_part(r"(?<=//)[\-a-z]+(?=\.)", self.root)
            cur_language = self.search_url_part(r"(?<=//)[\-a-z]+(?=\.)", url)
            # compare only parts that were really found, an url without them is not familiar
            same_value = bool(org_val_search) and org_val_search == cur_val_search
            other_language = bool(org_language) and bool(cur_language) and cur_language != org_language
            if (other_language and same_value) or re.findall(r"(?<=\.)m(?=\.)", url):
                return True
        elif re.findall(r"(?<=//)(m|([a-z]{2})+(-[a-z]{2})*)(?=\.)", url) or re.findall(r"(?<=/)[a-z]{2}$", url):
            return True
        return False

    def search_url_part(self, pattern: str, url: str) -> str:
        """
        return a part of an url by a pattern, or empty when the url does not contain him
        parameters:
            pattern (str): the regex of the part which is searched
            url (str): the url which from him the part is extracted
        returns:
            part (str): the found part of the url or an empty string
        """
        search = re.search(pattern, url)
        return search.group(0) if search else ''

    def create_child_datasets(self, father: str, childs: list[str], depth: int) -> list[dict]:
        """
        returns list of datasets from sub-urls in same depth level
        parameters:
            father (str): the url that is contains all sub-urls
            childs (list): list of sub-urls for father url
            depth (int): the depth level for the sub-urls
        returns:
            datasets (list): list of datasets is contains all sub-urls of a father url
        """
        datasets = []
        if not childs:
            return datasets
        # filter first, so only the urls which are really new are asked in the network
        new_childs = []
        for child in childs:
            if not (child in self.visited or self.is_ignore_url(child) or self.is_familiar_url(child)):
                self.visited.add(child)
                new_childs.append(child)
        # advance the bar for the urls which were filtered out without any request
        self.track["progress"]["per_url"]['value'] += ((len(childs) - len(new_childs)) / len(childs))
        # the access of urls which are scanned in the next depth is taken from that scan,
        # only urls of the last depth are checked here and with several threads together
        accesses = self.run_in_parallel(self.try_open_url, new_childs) if depth == self.max_depth else [None] * len(new_childs)
        for child, access in zip(new_childs, accesses):
            self.serial += 1
            dataset = self.insert_into_dataset(father, child, depth, access)
            datasets.append(dataset)
            self.track["progress"]["per_url"]['value'] += (1 / len(childs))
            self.track["progress"]["per_depth"]['value'] = self.track["progress"]["per_url"]['value'] if depth == 1 else None
        self.track["progress"]["per_url"]['value'] = 0
        return datasets

    def insert_into_dataset(self, father: str, child: str, depth: int, access: bool | None) -> dict[str, any]:
        """
        insert url server into dataset
        parameters:
            father (str): the url that is contains the sub-url
            child (str): sub-url of father url
            depth (int): depth level of the sub-url
            access (bool): if the url is approachable, None when it is filled from his scan
        returns:
            dataset (dict): collection data of sub-url
        """
        dataset = {
            "serial": 'url_' + str(self.serial),
            "father": father,
            "child": child,
            "depth": depth,
            "access": access
        }
        return dataset

    def read_data_offsprings(self, datasets: list[dict]) -> list[dict]:
        """
        download all data from main url up to max depth
        parameters:
            datasets (list): cumulative list of datasets that is contains the all data of the main
            url up to a current depth level
        returns:
            datasets (list): cumulative list of datasets that is contains the all data of the main
            url up to a max depth level
        """
        depth = datasets[len(datasets) - 1]['depth'] if datasets else self.max_depth
        if depth < self.max_depth:
            self.track["status"]["depth"].config(text=f'extract sub-urls in depth {depth + 1} from\n{self.root}')
            sub_url = 1
            cumulative = []
            # download all the pages of this depth with several threads together, the results
            # are received by order while the next pages are already on their way
            pages = self.run_in_parallel(self.read_page_data, [dataset['child'] for dataset in datasets])
            for dataset, (access, html) in zip(datasets, pages):
                father = dataset['child']
                # the download of the page supplies also the access of his url
                dataset['access'] = access
                self.track["status"]["quantity"].config(text=f'now extract sub-urls from url number {sub_url} out of {len(datasets)}\n{father}')
                new_datasets = self.extract_data_childs(dataset, html) if access else []
                if new_datasets:
                    cumulative = cumulative + new_datasets
                    self.track["added"]["sub-url"].config(text=f'were added {len(new_datasets)} more new sources')
                    self.track["so_far"]["count"] += len(new_datasets)
                    self.track["so_far"]["update"].config(text=f'number of sources in total so far in this depth is {self.track["so_far"]["count"]}')
                else:
                    self.track["added"]["sub-url"].config(text=f'does not exist sub-urls to this url')
                sub_url += 1
                self.track["progress"]["per_depth"]['value'] += (1 / len(datasets)) if depth > 0 else self.track["progress"]["per_depth"]['value']
            self.track["added"]["overall"].config(text=f'overall {len(cumulative)} sources in depth {depth + 1}')
            self.track["progress"]["per_depth"]['value'] = 0
            return datasets + self.read_data_offsprings(cumulative)
        elif depth == self.max_depth:
            # finished export urls progress message
            self.track["status"]["depth"].config(text=f'the export progress completed')
            return datasets
        else:
            raise ValueError(f'You entered a negative max depth')

    def build_result_file_path(self) -> str:
        """
        create path for result file
        returns:
            path (str): the final path that him will save all data of main url
        """
        name = self.root.split('.')[1]
        source = self.root.split('/')[-1].lower() if name == 'wikipedia' else name
        folder = "wikipedia" if name == 'wikipedia' else source
        path = "sources/urls/" + folder + "/" + source + "_md" + str(self.max_depth)
        return path

    def run_progress(self) -> str | list[dict]:
        """
        decide order of actions for progress
        returns:
            datasets (list): cumulative list of datasets that is contains the all data of the main
            url up to a max depth level
        """
        # check correctness of url
        if re.match(r"^http[s]?://[\w+\-/=(),?_#]+(\.[\w+\-/=(),?_#]+)+$", self.root):
            # init frame of url process
            self.pipeline_frame()
            # update all track widgets from process frame
            self.update_track_widgets()
            # build the path for result file
            path = self.build_result_file_path()
            # insert root server into dataset, his access is checked here only when he is
            # not scanned at all, otherwise it is taken from his scan
            access = self.try_open_url(self.root) if self.max_depth == 0 else None
            self.visited.add(self.root)
            init = self.insert_into_dataset('child input', self.root, 0, access)
            # read data offsprings of root from the cloud
            datasets = self.read_data_offsprings([init])
            # return data offsprings
            return path, datasets
        elif not self.root:
            raise IOError(f'Root url not inserted')
        else:
            raise IOError(f'You entered invalid url')
