# 包 digital_unit 1.5.4
（language：Chinese）
这是一个有关**数据的单位**的包,如长度、面积、体积等，可以用它来表示一个数量的单位
使用示例
``` python3
from digital_unit.Lenth import CentiMeter,MilliMeter
from digital_unit.root import Number

if __name__ == '__main__':
    _1cm = Number(1.0, CentiMeter()) # Create the data. Don't forget the parentheses!
    print(_1cm)
    _1cm.change_unit(MilliMeter()) # Changes to the unit. Don't forget the parentheses!
    print(_1cm)
```
使用`Number(NUMBER, UNIT())`来创建实例，使用`XXX.change_unit(NEWUNIT())`来修改单位。
## 1.5.4版本新增
CubicCentimeter（立方厘米），CubicDecimeter（立方分米），Liter（升），MilliLiter（毫升）,SquareDecimeter（平方分米）。

## 1.5.4版本修正
SquareCentiMeter（平方厘米）的进率。

# package digital_unit 1.5.4
(language: English)
This is **a unit of data** related to packages, such as length, area, volume, etc., it can be used to represent a number of units
Use the sample
```python3
from digital_unit. Lenth import CentiMeter, MilliMeter
from digital_unit. Root import Number

if __name__ = = "__main__" :
_1cm = Number (1.0 CentiMeter ()) # Create the data. Don 't forget the parentheses.
print (_1cm)
_1cm. Change_unit (MilliMeter ()) #Changes to the unit. Don 't forget the parentheses.
print (_1cm)
```
Using ` Number (NUBER, UNIT()) ` to create an instance, use ` XXX.Change_unit (NEWUNIT ()) ` to modify the UNIT

## Added in version 1.5.4
CubicCentimeter, CubicDecimeter, Liter, MilliLiter, SquareDecimeter.
## 1.5.4 Revision
The unit rate of SquareCentiMeter (square centimeters).