from operator import __ge__ 
from operator import __le__ 
from typing import Callable

from dataclasses import dataclass,field
import operator
from .Sensors import *

class Comperators():
    greater_equals = __ge__
    lower_equas = __le__



@dataclass
class Feedback():
    sensor : Sensor
    target_value : float
    comperator : Callable[[float, float], bool]
    def polling(self):
        return self.comperator(self.sensor.value, self.target_value)
    





