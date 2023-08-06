from enum import Enum as _Enum

class TimeEnum(_Enum):
    '''relative to seconds'''
    Second = 1
    Minute = 60
    Hour = Minute * 60
    Day = 24 * Hour


class TimeUnit():
    def __init__(self, amount: float, unit: TimeEnum):
        self.amount = amount
        self.unit = unit

    def To(self, desiredUnit: TimeEnum):
        return self.Converter(self.amount, self.unit, desiredUnit)

    @classmethod
    def Converter(cls, amount: float, unit: TimeEnum, desiredUnit: TimeEnum) -> 'TimeUnit':
        totalSeconds = amount * unit.value # since TimeEnum is relative to seconds, anything multiplied by it will result in seconds
        convertedAmount = totalSeconds / desiredUnit.value
        return TimeUnit(convertedAmount, desiredUnit)

    def __eq__(self, other) -> bool:
        if not isinstance(other, TimeUnit):
            return NotImplemented
        return self.To(TimeEnum.Second).amount == other.To(TimeEnum.Second).amount
    
    def __str__(self) -> str:
        return f'{round(self.amount, 2)} {self.unit.name}'