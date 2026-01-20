from abc import abstractmethod, ABC

from app.deformation.DeformationScan import DeformationScan


class DeformationCalculatorABC(ABC):

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def calculate(self, def_scan: DeformationScan):
        pass
