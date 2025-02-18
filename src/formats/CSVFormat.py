from src.client.format_process import FormatProcess
from src.formats.iformat import IFormat
import csv

class CSVFormat(FormatProcess, IFormat):

    def __init__(self, frame, path: str, datasets: list[dict]) -> None:
        """
        constructor for CSVFormat object
        attributes:
            path (str): the path to be saved all the cumulative main url data
            datasets (list): cumulative list of all the main url data
        """
        super().__init__(frame)
        self.path = path
        self.datasets = datasets
        self.fields = None
        self.results = None
        self.track = None

    def pipeline_progress(self) -> None:
        # initialize the rest of properties from the constructor
        self.initialize_properties()
        # normalize the data to the required format
        self.normalize_data()
        # write the data to the file of the format
        self.write_data_to_file()

    def initialize_properties(self) -> None:
        self.fields = list(self.datasets[0].keys())
        self.results = []
        tracks = self.frame.winfo_children()[17:]
        self.track = {
            "status": tracks[0],
            "convert": tracks[2]
        }

    def normalize_data(self) -> None:
        for dataset in self.datasets:
            self.results.append(list(dataset.values()))
            self.track["convert"]['value'] += 1
        self.track["convert"]['value'] = 0

    def write_data_to_file(self) -> None:
        with open(self.path, "w", encoding='utf8', newline='\n') as file:
            csv_writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_ALL)
            csv_writer.writerow(self.fields)
            csv_writer.writerows(self.results)
        # finished convert datasets progress message
        self.track["status"].config(text="the convert progress completed")
