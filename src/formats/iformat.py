from abc import ABCMeta, abstractmethod

class IFormat(metaclass=ABCMeta):

    @abstractmethod
    def pipeline_progress(self) -> None:
        """ progress for convert of datasets to readable format """
        pass

    @abstractmethod
    def initialize_properties(self) -> None:
        """ initialize rest attributes necessaries to process """
        pass

    @abstractmethod
    def normalize_data(self) -> None:
        """ normalize server data and write final data into file results """
        pass

    @abstractmethod
    def write_data_to_file(self) -> None:
        """ write all data to required format file """
        pass
