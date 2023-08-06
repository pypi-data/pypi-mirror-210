import json
import os
import simpleworkspace as sw
import unittest
from simpleworkspace.settingsproviders import SettingsManager_AutoMapped_JSON, SettingsManager_JSON, SettingsManager_BasicConfig
from configparser import ConfigParser 
from basetestcase import BaseTestCase




class CustomSettingsManager_JSON_WithDefaultValues(SettingsManager_JSON):
    Settings = {
        "testString": "str1",
        "testInt": 10,
        "testBool": True,
        "testList": ["a", "b", "c", [{"a2": 100}]]
    }
class CustomSettingsManager_Automapped_TypedSettings(SettingsManager_AutoMapped_JSON):
    Setting_testString = "str1"
    Setting_testInt = 10
    Setting_testBool = True
    Setting_testList = ["a", "b", "c", [{"a2": 100}]]

class SettingsProvidersTests(BaseTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.testSettingsPath = os.path.join(cls.testPath, "settings.anyextension")

    def test_SettingsManagerJSON_LoadsAndSavesCorrect(self):
        settingsManager = SettingsManager_JSON(self.testSettingsPath)
        self.assertEqual(len(settingsManager.Settings.keys()),  0)
        settingsManager.LoadSettings()
        settingsManager.Settings["test1"] = 10
        settingsManager.Settings["test2"] = 20
        settingsManager.SaveSettings()
        savedSettingData = sw.io.file.Read(settingsManager._settingsPath)
        obj = json.loads(savedSettingData)
        self.assertEqual(obj, {"test1": 10, "test2": 20})
        settingsManager = SettingsManager_JSON(settingsManager._settingsPath)
        settingsManager.LoadSettings()
        self.assertEqual(settingsManager.Settings["test1"],  10)
        self.assertEqual(settingsManager.Settings["test2"],  20)

    def test_SettingsManagerJSONWithDynamicSettings_LoadsCorrectly(self):
        settingsManager = CustomSettingsManager_JSON_WithDefaultValues(self.testSettingsPath)
        settingsManager.LoadSettings()  # nothing to load, should keep default settings
        self.assertEqual(settingsManager.Settings["testString"]          , "str1")
        self.assertEqual(settingsManager.Settings["testInt"]             , 10    )
        self.assertEqual(settingsManager.Settings["testBool"]            , True  )
        self.assertEqual(settingsManager.Settings["testList"][0]         , "a"   )
        self.assertEqual(settingsManager.Settings["testList"][3][0]["a2"], 100   )
        settingsManager.SaveSettings()

        # should still load the default settings that were saved previously
        settingsManager = CustomSettingsManager_JSON_WithDefaultValues(settingsManager._settingsPath)
        settingsManager.LoadSettings()  # should load same as default settings
        self.assertEqual(settingsManager.Settings["testString"]          , "str1")
        self.assertEqual(settingsManager.Settings["testInt"]             , 10    )
        self.assertEqual(settingsManager.Settings["testBool"]            , True  )
        self.assertEqual(settingsManager.Settings["testList"][0]         , "a"   )
        self.assertEqual(settingsManager.Settings["testList"][3][0]["a2"], 100   )

        sw.io.file.Create(settingsManager._settingsPath, json.dumps({"testInt": 999}))
        settingsManager = CustomSettingsManager_JSON_WithDefaultValues(settingsManager._settingsPath)
        settingsManager.LoadSettings()  # should load "testInt", should keep default settings
        self.assertEqual(settingsManager.Settings["testString"],  "str1")
        self.assertEqual(settingsManager.Settings["testInt"],  999)
        self.assertEqual(settingsManager.Settings["testBool"],  True)
        self.assertEqual(settingsManager.Settings["testList"][0],  "a")
        self.assertEqual(settingsManager.Settings["testList"][3][0]["a2"],  100)

        settingsManager.Settings["testList"][3][0]["a2"] = 200
        self.assertEqual(settingsManager.Settings["testList"][3][0]["a2"],  200)
        settingsManager.ClearSettings() #should restore default value, to ensure not same reference was used
        self.assertEqual(settingsManager.Settings["testList"][3][0]["a2"],  100)

    def test_SettingsManagerJSONWithTypedSettings_LoadsCorrectly(self):
        settingsManager = CustomSettingsManager_Automapped_TypedSettings(self.testSettingsPath)
        settingsManager.LoadSettings()  # nothing to load, should keep default settings
        self.assertEqual(settingsManager.Setting_testString          ,  "str1")
        self.assertEqual(settingsManager.Setting_testInt             ,  10)
        self.assertEqual(settingsManager.Setting_testBool            ,  True)
        self.assertEqual(settingsManager.Setting_testList[0]         ,  "a")
        self.assertEqual(settingsManager.Setting_testList[3][0]["a2"],  100)
        settingsManager.SaveSettings()

        # should still load the default settings that were saved previously
        settingsManager = CustomSettingsManager_Automapped_TypedSettings(settingsManager._settingsPath)
        settingsManager.LoadSettings()  # should load same as default settings
        self.assertEqual(settingsManager.Setting_testString          ,  "str1")
        self.assertEqual(settingsManager.Setting_testInt             ,  10)
        self.assertEqual(settingsManager.Setting_testBool            ,  True)
        self.assertEqual(settingsManager.Setting_testList[0]         ,  "a")
        self.assertEqual(settingsManager.Setting_testList[3][0]["a2"],  100)

        sw.io.file.Create(settingsManager._settingsPath, json.dumps({"testInt": 999}))
        settingsManager = CustomSettingsManager_Automapped_TypedSettings(settingsManager._settingsPath)
        settingsManager.LoadSettings()  # should load same all default except "testInt"
        self.assertEqual(settingsManager.Setting_testString          ,  "str1")
        self.assertEqual(settingsManager.Setting_testInt             ,  999)
        self.assertEqual(settingsManager.Setting_testBool            ,  True)
        self.assertEqual(settingsManager.Setting_testList[0]         ,  "a")
        self.assertEqual(settingsManager.Setting_testList[3][0]["a2"],  100)

        settingsManager.Setting_testList[3][0]["a2"] = 200
        self.assertEqual(settingsManager.Setting_testList[3][0]["a2"],  200)
        settingsManager.ClearSettings() #should restore default value, to ensure not same reference was used
        self.assertEqual(settingsManager.Setting_testList[3][0]["a2"],  100)
    
    def test_SettingsManager_BasicConfigParser_ParsesAndSavesProperly(self):
        settingsManager = SettingsManager_BasicConfig(self.testSettingsPath)
        settingsManager.LoadSettings()
        self.assertEqual(len(settingsManager.Settings.keys()), 0)

        settingsManager.Settings["key1"] = "value1"
        settingsManager.Settings["key2"] = "value2"
        settingsManager.SaveSettings()

        outputData = sw.io.file.Read(self.testSettingsPath)
        assert sw.utility.regex.Match("/^key1=value1$/", outputData)
        assert sw.utility.regex.Match("/^key2=value2$/", outputData)

    def test_SettingsManager_BasicConfigParser_HandlesCommentsCorrectly(self):
        # try parse a new file
        configFileData = "\n" #empty line
        configFileData += "# start comment\n"
        configFileData += " # also a comment, since whitespace are stripped\n"
        configFileData += "\n"
        configFileData += "#key1 comment\n"
        configFileData += "key1=value1         # inline comment\n"
        configFileData += "#key2 comment, here we add some spacing to ensure its not affected\n"
        configFileData += "  key2   =    value2     \n" #should be "key2": "value2"
        configFileData += "\n"
        configFileData += "### when you add new settings, they should be added below this comment ###\n"
        sw.io.file.Create(self.testSettingsPath, configFileData)
        settingsManager = SettingsManager_BasicConfig(self.testSettingsPath)
        settingsManager.LoadSettings()
        self.assertEqual(len(settingsManager.Settings.keys()), 2)
        self.assertEqual(settingsManager.Settings["key1"], "value1")
        self.assertEqual(settingsManager.Settings["key2"], "value2")

        #try export the config
        settingsManager.SaveSettings()
        outputLines = sw.io.file.Read(self.testSettingsPath).splitlines()
        self.assertEqual(outputLines[0], "")
        self.assertEqual(outputLines[1], "# start comment")
        self.assertEqual(outputLines[2], "# also a comment, since whitespace are stripped") # here the saved version should have left whitespace stripped
        self.assertEqual(outputLines[3], "")
        self.assertEqual(outputLines[4], "#key1 comment")
        self.assertEqual(outputLines[5], "key1=value1 # inline comment")
        self.assertEqual(outputLines[6], "#key2 comment, here we add some spacing to ensure its not affected")
        self.assertEqual(outputLines[7], "key2=value2") # all whitespaces stripped
        self.assertEqual(outputLines[8], "")
        self.assertEqual(outputLines[9], "### when you add new settings, they should be added below this comment ###")

        #add non existing settings before save to ensure they are added last
        settingsManager = SettingsManager_BasicConfig(self.testSettingsPath)
        settingsManager.LoadSettings()
        self.assertEqual(len(settingsManager.Settings.keys()), 2)
        self.assertEqual(settingsManager.Settings["key1"], "value1")
        self.assertEqual(settingsManager.Settings["key2"], "value2")

        settingsManager.Settings["key3"] = "value3"
        settingsManager.Settings["key4"] = "value4"
        settingsManager.SaveSettings()
        outputLines = sw.io.file.Read(self.testSettingsPath).splitlines()
        self.assertEqual(len(outputLines), 12)
        self.assertEqual(outputLines[0], "")
        self.assertEqual(outputLines[1], "# start comment")
        self.assertEqual(outputLines[2], "# also a comment, since whitespace are stripped") # here the saved version should have left whitespace stripped
        self.assertEqual(outputLines[3], "")
        self.assertEqual(outputLines[4], "#key1 comment")
        self.assertEqual(outputLines[5], "key1=value1 # inline comment")
        self.assertEqual(outputLines[6], "#key2 comment, here we add some spacing to ensure its not affected")
        self.assertEqual(outputLines[7], "key2=value2") # all whitespaces stripped
        self.assertEqual(outputLines[8], "")
        self.assertEqual(outputLines[9], "### when you add new settings, they should be added below this comment ###")
        
        newdata = '\n'.join(outputLines[10:12])
        assert sw.utility.regex.Match("/^key3=value3$/",newdata)
        assert sw.utility.regex.Match("/^key4=value4$/",newdata)

        settingsManager = SettingsManager_BasicConfig(self.testSettingsPath)
        settingsManager.LoadSettings()
        self.assertEqual(len(settingsManager.Settings.keys()), 4)
        self.assertEqual(settingsManager.Settings["key1"], "value1")
        self.assertEqual(settingsManager.Settings["key2"], "value2")
        self.assertEqual(settingsManager.Settings["key3"], "value3")
        self.assertEqual(settingsManager.Settings["key4"], "value4")
        del settingsManager.Settings["key1"]
        del settingsManager.Settings["key3"]

        settingsManager.SaveSettings()
        outputLines = sw.io.file.Read(self.testSettingsPath).splitlines()
        self.assertEqual(len(outputLines), 10)
        self.assertEqual(outputLines[0], "")
        self.assertEqual(outputLines[1], "# start comment")
        self.assertEqual(outputLines[2], "# also a comment, since whitespace are stripped") # here the saved version should have left whitespace stripped
        self.assertEqual(outputLines[3], "")
        self.assertEqual(outputLines[4], "#key1 comment")
        self.assertEqual(outputLines[5], "#key2 comment, here we add some spacing to ensure its not affected")
        self.assertEqual(outputLines[6], "key2=value2") # all whitespaces stripped
        self.assertEqual(outputLines[7], "")
        self.assertEqual(outputLines[8], "### when you add new settings, they should be added below this comment ###")
        self.assertEqual(outputLines[9], "key4=value4")

    @unittest.skip
    def test_SettingsManager_BasicConfigParser_PerformanceTesting(self):
        def CreateDummySettings():
            with open(self.testSettingsPath, "w") as fp:
                fp.write(f"[DEFAULT]\n")
                for i in range(100):
                    fp.write(f"key{i}=value{i}\n")

        sw1 = sw.utility.StopWatch()
        sw2 = sw.utility.StopWatch()
        sw3 = sw.utility.StopWatch()
        sw4 = sw.utility.StopWatch()



        for i in range(100):
            CreateDummySettings()
            sw1.Start()
            settingsManager = SettingsManager_BasicConfig("./out/settings.anyextension")
            settingsManager.LoadSettings()
            sw1.Stop()
            sw2.Start()
            settingsManager.SaveSettings()
            sw2.Stop()

            CreateDummySettings()
            sw3.Start()
            cnf = ConfigParser()
            cnf.read("./out/settings.anyextension")
            sw3.Stop()
            sw4.Start()
            with open("./out/settings.anyextension", "w") as f:
                cnf.write(f)
            sw4.Stop()

        result = f"basicConfig: {sw1.GetElapsedMilliseconds()} - {sw2.GetElapsedMilliseconds()} \n"
        result += f"python ConfigParser: {sw3.GetElapsedMilliseconds()} - {sw4.GetElapsedMilliseconds()} "
        self.assertTrue(False, result) #fail on purpose