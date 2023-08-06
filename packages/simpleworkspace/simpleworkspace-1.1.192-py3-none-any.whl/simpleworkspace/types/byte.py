from enum import Enum as _Enum
class ByteEnum(_Enum):
    '''relative to bytes'''
    Byte = 1
    KiloByte = 1000
    MegaByte = KiloByte * 1000
    GigaByte = MegaByte * 1000
    TeraByte = GigaByte * 1000

class ByteUnit():
    def __init__(self, amount:float, unit: ByteEnum):
        self.amount = amount
        self.unit = unit
    
    def To(self, desiredUnit:ByteEnum):
        return self.Converter(self.amount, self.unit, desiredUnit)
    
    @classmethod
    def Converter(cls, amount: float, unit: ByteEnum, desiredUnit: ByteEnum) -> 'ByteUnit':
        totalBytes = amount * unit.value #since ByteEnum is relative to bytes, anything multiplied by it will result in bytes
        convertedAmount = totalBytes / desiredUnit.value
        return ByteUnit(convertedAmount, desiredUnit)

    def __eq__(self, other) -> bool:
        if not isinstance(other, ByteUnit):
            return NotImplemented
        return self.To(ByteEnum.Byte).amount == other.To(ByteEnum.Byte).amount
        
    def __str__(self) -> str:
        return f'{round(self.amount, 2)} {self.unit.name}'
