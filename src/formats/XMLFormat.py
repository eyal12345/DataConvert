from src.client.format_process import FormatProcess
from src.formats.iformat import IFormat
import xml.etree.ElementTree as ET

class XMLFormat(FormatProcess, IFormat):

    def __init__(self, frame, path: str, datasets: list[dict]) -> None:
        """
        constructor for XMLFormat object
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
        self.results = ET.Element("data")
        tracks = self.frame.winfo_children()[17:]
        self.track = {
            "status": tracks[0],
            "convert": tracks[2]
        }

    def normalize_data(self) -> None:
        key = self.datasets[0][self.fields[0]].split('_')[0]
        for dataset in self.datasets:
            elem = ET.SubElement(self.results, key)
            elem.set('id', str(next))
            for i in range(1, len(dataset)):
                ET.SubElement(elem, self.fields[i]).text = str(dataset[self.fields[i]])
            self.track["convert"]['value'] += 1
        self.track["convert"]['value'] = 0

    def write_data_to_file(self) -> None:
        tree = ET.ElementTree(self.results)
        ET.indent(tree, space="\t", level=0)
        tree.write(self.path, xml_declaration=True, encoding="utf-8")
        # finished convert datasets progress message
        self.track["status"].config(text="the convert progress completed")
