from src.client.format_process import FormatProcess
from src.formats.TextFormat import TextFormat
from src.formats.CSVFormat import CSVFormat
from src.formats.JsonFormat import JsonFormat
from src.formats.YmlFormat import YmlFormat
from src.formats.XMLFormat import XMLFormat
from src.formats.XLSXFormat import XLSXFormat
from src.formats.DBFormat import DBFormat

class FormatServer(FormatProcess):

    def __init__(self, frame, path: str, datasets: list[dict], written=10) -> None:
        """
        constructor for Format object
        attributes:
            path (str): the path to be saved all the cumulative main url data
            datasets (list): cumulative list of all the main url data
        """
        super().__init__(frame)
        self.written = written
        self.path = path
        self.datasets = datasets
        self.format = self.path.split('.')[-1]
        self.status = None
        self.convert = None

    def create_file_results(self) -> None:
        """ create results file by user's format """
        # define instance for each format
        instances = {
            'txt': TextFormat(self.frame, self.path, self.datasets),
            'csv': CSVFormat(self.frame, self.path, self.datasets),
            'json': JsonFormat(self.frame, self.path, self.datasets),
            'yml': YmlFormat(self.frame, self.path, self.datasets),
            'xml': XMLFormat(self.frame, self.path, self.datasets),
            'xlsx': XLSXFormat(self.frame, self.path, self.datasets),
            'db': DBFormat(self.frame, self.path, self.datasets)
        }
        # check if user's format found is valid and write to file
        if self.format in instances.keys():
            instances[self.format].pipeline_progress()
        else:
            raise IOError("the your format is invalid")

    def run_progress(self) -> None:
        # init frame of convert process
        self.pipeline_frame()
        # create results file by user's format
        self.create_file_results()
