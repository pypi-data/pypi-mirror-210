import json
import simpleworkspace as sw
from basetestcase import BaseTestCase
from simpleworkspace.types.byte import ByteUnit, ByteEnum
from simpleworkspace.types.time import TimeEnum, TimeUnit

class TimeTests(BaseTestCase):
    def test_Times_HasCorrectSeconds(self):
        self.assertEqual(TimeEnum.Day.value    * 2, 172800)
        self.assertEqual(TimeEnum.Hour.value   * 2, 7200)
        self.assertEqual(TimeEnum.Minute.value * 2, 120)
        
    def test_TimeUnit_KnownEqualityChecks(self):
        self.assertEqual(TimeUnit(2, TimeEnum.Minute),
                         TimeUnit(120, TimeEnum.Second))
        
        convertedUnit = TimeUnit(86400, TimeEnum.Second)
        convertedUnit_toMinute = TimeUnit(1440, TimeEnum.Minute)
        convertedUnit_toHour = convertedUnit_toMinute.To(TimeEnum.Hour)
        convertedUnit_toDay = convertedUnit_toHour.To(TimeEnum.Day)
        self.assertEqual(convertedUnit, TimeUnit(86400, TimeEnum.Second))
        self.assertEqual(convertedUnit_toMinute, TimeUnit(1440, TimeEnum.Minute))
        self.assertEqual(convertedUnit_toHour, TimeUnit(24, TimeEnum.Hour))
        self.assertEqual(convertedUnit_toDay, TimeUnit(1, TimeEnum.Day))

        self.assertEqual(TimeUnit(2, TimeEnum.Hour).To(TimeEnum.Minute),
                         TimeUnit(120, TimeEnum.Minute))

    def test_TimeUnit_NegativeEqualityChecks(self):
        self.assertNotEqual(TimeUnit(2, TimeEnum.Minute),
                            TimeUnit(2, TimeEnum.Second))
        
        self.assertNotEqual(TimeUnit(2, TimeEnum.Minute),
                            TimeUnit(3, TimeEnum.Minute))
        
    def test_TimeUnit_StrictEqualityCheck(self):
        
        convertedUnit = ByteUnit(1024, ByteEnum.Byte).To(ByteEnum.KiloByte)
        self.assertEqual(convertedUnit.amount, 1.024)
        self.assertEqual(convertedUnit.unit, ByteEnum.KiloByte)

        t = TimeUnit(86400, TimeEnum.Second).To(TimeEnum.Hour)
        self.assertEqual(t.amount, 24)
        self.assertEqual(t.unit, TimeEnum.Hour)

        t = TimeUnit(24, TimeEnum.Hour).To(TimeEnum.Second)
        self.assertEqual(t.amount, 86400)
        self.assertEqual(t.unit, TimeEnum.Second)


        t = TimeUnit(86400, TimeEnum.Second)
        assert t.To(TimeEnum.Second).amount == 86400
        assert t.To(TimeEnum.Minute).amount == 1440
        assert t.To(TimeEnum.Hour  ).amount == 24
        assert t.To(TimeEnum.Day   ).amount == 1

        t = TimeUnit(1440, TimeEnum.Minute)
        assert t.To(TimeEnum.Second).amount == 86400
        assert t.To(TimeEnum.Minute).amount == 1440
        assert t.To(TimeEnum.Hour  ).amount == 24
        assert t.To(TimeEnum.Day   ).amount == 1

        t = TimeUnit(24, TimeEnum.Hour)
        assert t.To(TimeEnum.Second).amount == 86400
        assert t.To(TimeEnum.Minute).amount == 1440
        assert t.To(TimeEnum.Hour  ).amount == 24
        assert t.To(TimeEnum.Day   ).amount == 1

        t = TimeUnit(1, TimeEnum.Day)
        assert t.To(TimeEnum.Second).amount == 86400
        assert t.To(TimeEnum.Minute).amount == 1440
        assert t.To(TimeEnum.Hour  ).amount == 24
        assert t.To(TimeEnum.Day   ).amount == 1
        

class ByteTests(BaseTestCase):
    def test_ByteUnit_KnownEqualityChecks(self):
        # Test conversions from Byte to other units
        
        self.assertEqual(ByteUnit(1, ByteEnum.Byte).To(ByteEnum.KiloByte), 
                         ByteUnit(0.001, ByteEnum.KiloByte))
        
        self.assertEqual(ByteUnit(1, ByteEnum.Byte).To(ByteEnum.MegaByte),
                         ByteUnit(0.000001, ByteEnum.MegaByte))
        
        self.assertEqual(ByteUnit(1, ByteEnum.Byte).To(ByteEnum.GigaByte), 
                         ByteUnit(0.000000001, ByteEnum.GigaByte))
        
        self.assertEqual(ByteUnit(1, ByteEnum.Byte).To(ByteEnum.TeraByte), 
                         ByteUnit(0.000000000001, ByteEnum.TeraByte))

        # Test conversions from KiloByte to other units
        self.assertEqual(ByteUnit(1000, ByteEnum.KiloByte).To(ByteEnum.Byte), 
                         ByteUnit(1000000, ByteEnum.Byte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.KiloByte).To(ByteEnum.MegaByte), 
                         ByteUnit(1, ByteEnum.MegaByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.KiloByte).To(ByteEnum.GigaByte), 
                         ByteUnit(0.001, ByteEnum.GigaByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.KiloByte).To(ByteEnum.TeraByte), 
                         ByteUnit(0.000001, ByteEnum.TeraByte))

        # Test conversions from MegaByte to other units
        self.assertEqual(ByteUnit(1000, ByteEnum.MegaByte).To(ByteEnum.Byte), 
                         ByteUnit(1000000000, ByteEnum.Byte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.MegaByte).To(ByteEnum.KiloByte), 
                         ByteUnit(1000000, ByteEnum.KiloByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.MegaByte).To(ByteEnum.GigaByte), 
                         ByteUnit(1, ByteEnum.GigaByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.MegaByte).To(ByteEnum.TeraByte), 
                         ByteUnit(0.001, ByteEnum.TeraByte))

        # Test conversions from GigaByte to other units
        self.assertEqual(ByteUnit(1000, ByteEnum.GigaByte).To(ByteEnum.Byte), 
                         ByteUnit(1000000000000, ByteEnum.Byte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.GigaByte).To(ByteEnum.KiloByte), 
                         ByteUnit(1000000000, ByteEnum.KiloByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.GigaByte).To(ByteEnum.MegaByte), 
                         ByteUnit(1000000, ByteEnum.MegaByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.GigaByte).To(ByteEnum.TeraByte), 
                         ByteUnit(1, ByteEnum.TeraByte))

        # Test conversions from TerraByte to other units
        self.assertEqual(ByteUnit(1000, ByteEnum.TeraByte).To(ByteEnum.Byte), 
                         ByteUnit(1000000000000000, ByteEnum.Byte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.TeraByte).To(ByteEnum.KiloByte), 
                         ByteUnit(1000000000000, ByteEnum.KiloByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.TeraByte).To(ByteEnum.MegaByte), 
                         ByteUnit(1000000000, ByteEnum.MegaByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.TeraByte).To(ByteEnum.GigaByte), 
                         ByteUnit(1000000, ByteEnum.GigaByte))


        # Test conversions between all possible units
        self.assertEqual(ByteUnit(1024, ByteEnum.Byte).To(ByteEnum.KiloByte),
                         ByteUnit(1.024, ByteEnum.KiloByte))
        
        self.assertEqual(ByteUnit(1.024, ByteEnum.KiloByte).To(ByteEnum.Byte),
                         ByteUnit(1024, ByteEnum.Byte))
        
        self.assertEqual(ByteUnit(1, ByteEnum.MegaByte).To(ByteEnum.GigaByte),
                         ByteUnit(0.001, ByteEnum.GigaByte))
        
        self.assertEqual(ByteUnit(100, ByteEnum.GigaByte).To(ByteEnum.TeraByte),
                         ByteUnit(0.1, ByteEnum.TeraByte))
        
        self.assertEqual(ByteUnit(2000, ByteEnum.KiloByte).To(ByteEnum.MegaByte),
                        ByteUnit(2, ByteEnum.MegaByte))
        
        self.assertEqual(ByteUnit(2, ByteEnum.MegaByte).To(ByteEnum.KiloByte),
                         ByteUnit(2000, ByteEnum.KiloByte))
        
    def test_ByteUnit_NegativeEqualityChecks(self):
        # Test conversions between all possible units
        self.assertNotEqual(ByteUnit(1024, ByteEnum.Byte).To(ByteEnum.KiloByte),
                         ByteUnit(1024, ByteEnum.KiloByte))
        
        self.assertNotEqual(ByteUnit(1.024, ByteEnum.KiloByte).To(ByteEnum.Byte),
                         ByteUnit(1.024, ByteEnum.Byte))
        
        self.assertNotEqual(ByteUnit(1, ByteEnum.MegaByte).To(ByteEnum.GigaByte),
                         ByteUnit(1, ByteEnum.GigaByte))
        
        self.assertNotEqual(ByteUnit(100, ByteEnum.GigaByte).To(ByteEnum.TeraByte),
                         ByteUnit(100, ByteEnum.TeraByte))
        
        self.assertNotEqual(ByteUnit(2000, ByteEnum.KiloByte).To(ByteEnum.MegaByte),
                        ByteUnit(2000, ByteEnum.MegaByte))
        
        self.assertNotEqual(ByteUnit(2, ByteEnum.MegaByte).To(ByteEnum.KiloByte),
                         ByteUnit(2, ByteEnum.KiloByte))

    def test_ByteUnit_EqualityChecksWithDiffentUnits(self):
        # Test conversions between all possible units
        self.assertEqual(ByteUnit(1024, ByteEnum.Byte),
                         ByteUnit(1.024, ByteEnum.KiloByte))
        
        self.assertEqual(ByteUnit(1.024, ByteEnum.KiloByte),
                         ByteUnit(1024, ByteEnum.Byte))
        
        self.assertEqual(ByteUnit(1, ByteEnum.MegaByte),
                         ByteUnit(0.001, ByteEnum.GigaByte))
        
        self.assertEqual(ByteUnit(100, ByteEnum.GigaByte),
                         ByteUnit(0.1, ByteEnum.TeraByte))
        
        self.assertEqual(ByteUnit(2000, ByteEnum.KiloByte),
                        ByteUnit(2, ByteEnum.MegaByte))
        
        self.assertEqual(ByteUnit(2, ByteEnum.MegaByte),
                         ByteUnit(2000, ByteEnum.KiloByte))
        
    def test_ByteUnit_StrictEqualityCheck(self):
        byteUnit = ByteUnit(5, ByteEnum.MegaByte)
        self.assertEqual(byteUnit.To(ByteEnum.Byte).amount    , 5000000)
        self.assertEqual(byteUnit.To(ByteEnum.KiloByte).amount, 5000)
        self.assertEqual(byteUnit.To(ByteEnum.MegaByte).amount, 5)
        self.assertEqual(byteUnit.To(ByteEnum.GigaByte).amount, 0.005)
        self.assertEqual(byteUnit.To(ByteEnum.TeraByte).amount, 0.000005)

        # Test conversions between all possible units
        convertedUnit = ByteUnit(1024, ByteEnum.Byte).To(ByteEnum.KiloByte)
        self.assertEqual(convertedUnit.amount, 1.024)
        self.assertEqual(convertedUnit.unit, ByteEnum.KiloByte)

        convertedUnit = ByteUnit(1.024, ByteEnum.KiloByte).To(ByteEnum.Byte)
        self.assertEqual(convertedUnit.amount, 1024)
        self.assertEqual(convertedUnit.unit, ByteEnum.Byte)

        convertedUnit = ByteUnit(1, ByteEnum.MegaByte).To(ByteEnum.GigaByte)
        self.assertEqual(convertedUnit.amount, 0.001)
        self.assertEqual(convertedUnit.unit, ByteEnum.GigaByte)

        convertedUnit = ByteUnit(100, ByteEnum.GigaByte).To(ByteEnum.TeraByte)
        self.assertEqual(convertedUnit.amount, 0.1)
        self.assertEqual(convertedUnit.unit, ByteEnum.TeraByte)

        convertedUnit = ByteUnit(2000, ByteEnum.KiloByte).To(ByteEnum.MegaByte)
        self.assertEqual(convertedUnit.amount, 2)
        self.assertEqual(convertedUnit.unit, ByteEnum.MegaByte)

        convertedUnit = ByteUnit(2, ByteEnum.MegaByte).To(ByteEnum.KiloByte)
        self.assertEqual(convertedUnit.amount, 2000)
        self.assertEqual(convertedUnit.unit, ByteEnum.KiloByte)