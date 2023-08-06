from .root import DigitalUnit
class Area(DigitalUnit):
    def __init__(self) -> None:
        self.type = 'Area'

class SquareMeter(Area):
    def __init__(self) -> None:
        super().__init__()
        self.measure = 1.0 
    def __str__(self) -> str:
        return 'm²'

class SquareKiloMeter(Area):
    def __init__(self) -> None:
        super().__init__()
        self.measure = 1000_000.0
    def __str__(self) -> str:
        return 'km²'

class Hectare(Area):
    def __init__(self) -> None:
        super().__init__()
        self.measure = 10_000.0
    def __str__(self) -> str:
        return 'hm²'

class SquareCentiMeter(Area):
    def __init__(self) -> None:
        super().__init__()
        self.measure = 1.0
    def __str__(self) -> str:
        return 'cm²'


    