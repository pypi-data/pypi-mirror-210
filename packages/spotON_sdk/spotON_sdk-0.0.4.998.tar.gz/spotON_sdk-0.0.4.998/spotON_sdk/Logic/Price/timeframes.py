from re import L
from pydantic import BaseModel, validator
from typing import List, Tuple
from datetime import datetime, time



class Timeframe(BaseModel):
    start: int
    end: int

    @validator('*')
    def validate_hours(cls, value):
        if not 0 <= value < 24:
            raise ValueError("hours should be in range 0-23")
        return value


class Timeframes(BaseModel):
    timeframes: List[Timeframe] =  [Timeframe(start=0, end=23)]

    @property
    def possible_hours(self):
        hours = set()
        for timeframe in self.timeframes:
            start, end = timeframe.start, timeframe.end
            if start <= end:
                hours.update(range(start, end))
            else:  # the timeframe goes over midnight
                hours.update(range(start, 24))
                hours.update(range(0, end))
        return sorted(list(hours))


    def add_timeframe(self, start: int, end: int):
        self.timeframes.append(Timeframe(start=start, end=end))

    def remove_timeframe(self, start: int, end: int):
        self.timeframes = [timeframe for timeframe in self.timeframes if not (timeframe.start == start and timeframe.end == end)]
    
    def remove_initial_timeframe(self):
        self.timeframes = self.timeframes[1:]

    def set_whole_day(self):
        self.timeframes.append(Timeframe(start=0, end=23))

    def set_morning(self):
        self.timeframes.append(Timeframe(start=5, end=12))

    def set_afternoon(self):
        self.timeframes.append(Timeframe(start=12, end=17))

    def set_evening(self):
        self.timeframes.append(Timeframe(start=17, end=20))

    def set_night(self):
        self.timeframes.append(Timeframe(start=20, end=5))

