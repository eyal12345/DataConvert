from src.client.url_process import URLProcess
import requests
import re

class URLServer(URLProcess):

    def __init__(self, frame, root: str, max_depth: int) -> None:
        """
        constructor for URL object
        attributes:
            root (str): the main url to be extracted all sub-urls up to max depth level
            max_depth (int): the depth level to be extracted sub-urls up to him
            format (str): the configuration data file for the item
            serial (int): the id number for a new url
            visited (list): cumulative list of urls that is checked
        """
        super().__init__(frame)
        self.root = root
        self.max_depth = max_depth
        self.serial = 0
        self.visited = []
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

    def try_open_url(self, url: str) -> bool:
        """
        return if url is valid access
        parameters:
            url (str): an url which is checked if is valid
        returns:
            True or False (bool): if a status code constitutes an approach to url
        """
        try:
            access = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=False)
            return access.status_code in [200, 301, 302, 303, 403, 406, 500, 999]
        except requests.exceptions.HTTPError:
            return False
        except requests.exceptions.SSLError:
            return False
        except requests.exceptions.ProxyError:
            return False
        except requests.exceptions.ConnectTimeout:
            return False
        except requests.exceptions.ConnectionError:
            return False

    def extract_data_childs(self, dataset: dict[str, any]) -> list[dict]:
        """
        extract data sub-urls set from each url in the dataset
        parameters:
            dataset (dict): data of sub-url which from him extract all sub-urls which is contains
        returns:
            datasets (list): collection of sub-urls in same depth level from the main url
        """
        father, depth = dataset['child'], dataset['depth']
        datasets = []
        try:
            response = requests.get(father, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=False)
            html = response.content.decode('latin1')
            urls = re.findall(r'(?<=href=")[https:]*[/{1,2}#]*[\w+.\-/=?_#]*(?=")', html)
            if urls:
                self.track["added"]["sub-url"].config(text=f'waiting to new sources from this url')
                childs = self.fix_urls(father, urls)
                datasets = self.create_child_datasets(father, childs, depth + 1)
            return datasets
        except requests.exceptions.HTTPError:
            return []

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
            org_val_search = re.search(r"(?<=/)[\-\.()\w\d]+$", self.root).group(0)
            cur_val_search = re.search(r"(?<=/)[\-\.()\w\d]+$", url).group(0)
            org_language = re.search(r"(?<=//)[\-a-z]+(?=\.)", self.root).group(0)
            cur_language = re.search(r"(?<=//)[\-a-z]+(?=\.)", url).group(0)
            if (cur_language != org_language and cur_val_search == org_val_search) or re.findall(r"(?<=\.)m(?=\.)", url):
                return True
        elif re.findall(r"(?<=//)(m|([a-z]{2})+(-[a-z]{2})*)(?=\.)", url) or re.findall(r"(?<=/)[a-z]{2}$", url):
            return True
        return False

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
        for child in childs:
            if not (child in self.visited or self.is_ignore_url(child) or self.is_familiar_url(child)):
                self.serial += 1
                dataset = self.insert_into_dataset(father, child, depth)
                datasets.append(dataset)
            self.track["progress"]["per_url"]['value'] += (1 / len(childs))
            self.track["progress"]["per_depth"]['value'] = self.track["progress"]["per_url"]['value'] if depth == 1 else None
        self.track["progress"]["per_url"]['value'] = 0
        return datasets

    def insert_into_dataset(self, father: str, child: str, depth: int) -> dict[str, any]:
        """
        insert url server into dataset
        parameters:
            father (str): the url that is contains the sub-url
            child (str): sub-url of father url
            depth (int): depth level of the sub-url
        returns:
            dataset (dict): collection data of sub-url
        """
        access = self.try_open_url(child)
        self.visited.append(child)
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
            for dataset in datasets:
                father, access = dataset['child'], dataset['access']
                self.track["status"]["quantity"].config(text=f'now extract sub-urls from url number {sub_url} out of {len(datasets)}\n{father}')
                new_datasets = self.extract_data_childs(dataset) if access else []
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

    def run_progress(self) -> str and list[dict]:
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
            # insert root server into dataset
            init = self.insert_into_dataset('child input', self.root, 0)
            # read data offsprings of root from the cloud
            datasets = self.read_data_offsprings([init])
            # return data offsprings
            return path, datasets
        elif not self.root:
            raise IOError(f'Root url not inserted')
        else:
            raise IOError(f'You entered invalid url')
