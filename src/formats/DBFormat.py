from src.client.format_process import FormatProcess
from src.formats.iformat import IFormat
from src.tools.DBConnection import DBConnection

class DBFormat(FormatProcess, IFormat):

    def __init__(self, frame, path: str, datasets: list[dict]) -> None:
        """
        constructor for DBFormat object
        attributes:
            path (str): the path to be saved all the cumulative main url data
            datasets (list): cumulative list of all the main url data
        """
        super().__init__(frame)
        self.path = path
        self.datasets = datasets
        self.fields = None
        self.cur = None
        self.track = None

    def pipeline_progress(self) -> None:
        # initialize the rest of properties from the constructor
        self.initialize_properties()
        # convert primitive types by sql types
        self.create_table_types()
        # normalize the data to the required format
        self.normalize_data()
        # write the data to the file of the format
        self.write_data_to_file()

    def initialize_properties(self) -> None:
        self.fields = list(self.datasets[0].keys())
        self.cur = DBConnection(self.path)
        tracks = self.frame.winfo_children()[17:]
        self.track = {
            "status": tracks[0],
            "convert": tracks[2]
        }

    def create_table_types(self) -> None:
        sql_convert_types = {
            'int': 'INTEGER',
            'str': 'TEXT',
            'bool': 'BOOLEAN'
        }
        types = {field: sql_convert_types[type(self.datasets[0][field]).__name__] for field in self.fields}
        self.cur.create_table(types)

    def normalize_data(self) -> None:
        for dataset in self.datasets:
            self.cur.insert_query(list(dataset.values()))
            self.track["convert"]['value'] += 1
        self.track["convert"]['value'] = 0

    def write_data_to_file(self) -> None:
        self.cur.__exit__()
        # finished convert datasets progress message
        self.track["status"].config(text="the convert progress completed")
