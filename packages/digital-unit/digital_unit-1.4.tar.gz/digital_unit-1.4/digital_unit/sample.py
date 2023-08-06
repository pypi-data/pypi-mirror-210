from digital_unit.Lenth import *
from digital_unit.root import *

if __name__ == '__main__':
    _1cm = Number(1.0, CentiMeter()) # Create the data. Don't forget the parentheses!
    print(_1cm)
    _1cm.change_unit(MilliMeter()) # Changes to the unit. Don't forget the parentheses!
    print(_1cm)