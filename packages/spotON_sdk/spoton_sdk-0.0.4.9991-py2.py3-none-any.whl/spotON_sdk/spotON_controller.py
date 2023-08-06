from typing import List
from dataclasses import dataclass


from spotON_sdk.Logic.Feedback import Feedback
from spotON_sdk.Logic.Output import Switchtypes
from spotON_sdk.Logic.Price import Price_Logic


@dataclass
class Controller():
    name :str
    config  : Price_Logic
    feedback : List[Feedback]
    output_Switch : Switchtypes