from .root import DigitalUnit

class Volume(DigitalUnit):
    def __init__(self) -> None:
        self.type = 'Volume'

class CubicMeter(Volume):
    def __init__(self) -> None:
        super().__init__()
        self.measure = 1.0 
    def __str__(self) -> str:
        return 'm³'