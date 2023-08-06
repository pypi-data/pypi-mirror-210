from .root import DigitalUnit

class Lenth(DigitalUnit):
    def __init__(self) -> None:
        self.type = 'Lenth'

class Metre(Lenth):
    def __init__(self) -> None:
        super().__init__()
        self.measure = 1.0
    def __str__(self) -> str:
        return 'm'

class KiloMetre(Lenth):
    def __init__(self) -> None:
        super().__init__()
        self.measure = 1000.0
    def __str__(self) -> str:
        return 'km'

class CentiMeter(Lenth):
    def __init__(self) -> None:
        super().__init__()
        self.measure = 0.01
    def __str__(self) -> str:
        return 'cm'

class MilliMeter(Lenth):
    def __init__(self) -> None:
        super().__init__()
        self.measure = 0.001
    def __str__(self) -> str:
        return 'mm'
