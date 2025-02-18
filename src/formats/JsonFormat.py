from src.client.format_process import FormatProcess
from src.formats.iformat import IFormat
import json

class JsonFormat(FormatProcess, IFormat):

    def __init__(self, frame, path: str, datasets: list[dict]) -> None:
        """
        constructor for JsonFormat object
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
        self.results = {}
        tracks = self.frame.winfo_children()[17:]
        self.track = {
            "status": tracks[0],
            "convert": tracks[2]
        }

    def normalize_data(self) -> None:
        for dataset in self.datasets:
            key = dataset[self.fields[0]]
            values = {self.fields[i]: dataset[self.fields[i]] for i in range(1, len(dataset))}
            self.results[key] = values
            self.track["convert"]['value'] += 1
        self.track["convert"]['value'] = 0

    def write_data_to_file(self) -> None:
        with open(self.path, "w", encoding='utf8') as file:
            json.dump(self.results, file, indent=4)
        # finished convert datasets progress message
        self.track["status"].config(text="the convert progress completed")
