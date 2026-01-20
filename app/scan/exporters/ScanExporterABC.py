from abc import ABC, abstractmethod


class ScanExporterABC(ABC):

    def __init__(self, file_path, *args, **kwargs):
        self.file_path = file_path

    @abstractmethod
    def export(self, scan):
        pass
