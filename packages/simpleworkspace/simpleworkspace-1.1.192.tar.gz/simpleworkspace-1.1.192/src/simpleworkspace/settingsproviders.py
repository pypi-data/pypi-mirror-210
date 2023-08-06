from abc import ABC as _ABC, abstractmethod as _abstractmethod
import os as _os
import json as _json
import simpleworkspace.io.file
from copy import deepcopy as _deepcopy

class SettingsManager_Base(_ABC):
    Settings = {}
    _cached_DefaultSettings = {}
    def __init__(self, settingsPath):
        self._settingsPath = settingsPath
        self._CacheDefaultSettings()

    def _CacheDefaultSettings(self):
        self._cached_DefaultSettings = _deepcopy(self.Settings)

    @_abstractmethod
    def _ParseSettingsFile(self, filepath) -> dict:
        '''responsible for parsing setting file and returning a settings object'''
    @_abstractmethod
    def _ExportSettingsFile(self, settingsObject: dict, outputPath: str):
        '''responsible for saving the settingsObject to file location in self._settingsPath'''
  
    def ClearSettings(self):
        self.Settings = _deepcopy(self._cached_DefaultSettings)

    def LoadSettings(self):
        '''Loads the setting file from specified location to the memory at self.settings'''
        self.ClearSettings()
        if not (_os.path.exists(self._settingsPath)):
            return

        settingsObject = self._ParseSettingsFile(self._settingsPath)
        #instead of replacing all the settings, we set it to default state, and copy over keys
        #incase default settings are specified/overriden, even if only one of the default setting existed in the file
        #we will keep other default settings as specified and only change value of new settings parsed
        self.Settings.update(settingsObject) 
        return

    def SaveSettings(self):
        self._ExportSettingsFile(self.Settings, self._settingsPath)


class SettingsManager_JSON(SettingsManager_Base):
    def _ParseSettingsFile(self, filepath):
        return _json.loads(simpleworkspace.io.file.Read(filepath))

    def _ExportSettingsFile(self, settingsObject, outputPath):
        jsonData = _json.dumps(settingsObject)
        simpleworkspace.io.file.Create(outputPath, jsonData)
        return


class SettingsManager_BasicConfig(SettingsManager_Base):
    '''
        Basic Config files are the simplest form of KeyValuePair config files.
        * each line consists of "key=value" pair.
        * comments can be placed anywhere with '#' both at start of a line or inline after a setting
        * whitespaces are trimmed from start and end of both key and the value. "key=value" is same as " key = value "
        * This parser is intentionally not compatible with INI format (will throw an exception only if a section is detected).
          The reason behind this is that basic config files don't use sections and therefore rely that every setting key is 
          unique. An INI file on the other hand can have same setting key under different sections.
    '''

    _fileLineOrdering = [] #tracks positions of lines to be able to preserve comments
    _fileLineOrderCounter = 0
    
    def _AddFileLineOrder(self, data, type):
        self._fileLineOrdering.append((self._fileLineOrderCounter, data, type)) #indexes: 0 = order, 1 = data, 2 = type of data
        self._fileLineOrderCounter += 1
    
    def _ResetFileLineOrder(self):
        self._fileLineOrdering = []
        self._fileLineOrderCounter = 0

    def _ParseSettingsFile(self, filepath):
        self._ResetFileLineOrder()
        conf = {}
        with open(filepath) as fp:
            for lineNo, line in enumerate(fp, start=1):
                line = line.strip()

                if line == '': #only a blank line
                    self._AddFileLineOrder(None, None)
                    continue
                elif line.startswith('#'): #only a comment line
                    self._AddFileLineOrder(line, "comment")
                    continue

                keyValueAndComment = line.split('#', 1)
                hasInlineComment = True if len(keyValueAndComment) == 2 else False
                if(hasInlineComment):
                    line = keyValueAndComment[0]
                keyValue = line.split('=', 1)
                if(len(keyValue) != 2):
                    raise ValueError(f"file contains bad line format [LineNo:{lineNo}]: key/value pair is not separated with '='")

                key = keyValue[0].strip()
                val = keyValue[1].strip()
                conf[key] = val
                if(hasInlineComment): #it had an inline comment
                    self._AddFileLineOrder([key, keyValueAndComment[1]], "key,comment")
                else:    #regular key value pair
                    self._AddFileLineOrder(key, "key")
        return conf

    def _ExportSettingsFile(self, settingsObject, outputPath):
        allKeys = set(settingsObject.keys())
        with open(outputPath, "w", newline='\n') as fp:
            for orderLine in self._fileLineOrdering:
                order, data, type = orderLine
                if(type is None):
                    fp.write("\n")
                elif(type == "comment"):
                    fp.write(data + "\n")
                elif(type == "key" and data in allKeys): #write out all previously existing keys
                    fp.write(f"{data}={settingsObject[data]}\n")
                    allKeys.remove(data)
                elif(type == "key,comment" and data[0] in allKeys):
                    key, comment = data[0], data[1] 
                    fp.write(f"{key}={settingsObject[key]} #{comment}\n")
                    allKeys.remove(key)
            for newKey in allKeys:
                fp.write(f"{newKey}={settingsObject[newKey]}\n")


            
        return

class SettingsManager_AutoMapped_JSON(_ABC):
    '''
    SettingsManager class that helps with accessing settings file in an abstract and simplified way.
    All derived classes automatically implement automapper of typed settings, where properties starting with "Setting_XXX"
    will automatically be loaded/exported.
    '''
    _cached_DefaultSettings = {}

    def __init__(self, settingsPath):
        self._settingsPath = settingsPath
        self._CacheDefaultSettings()

    def _CacheDefaultSettings(self):
        settingsObject = self._ExportTypedSettings()
        self._cached_DefaultSettings = _deepcopy(settingsObject)

    def _ParseSettingsFile(self, filepath):
        '''responsible for parsing setting file and returning a settings object'''
        return _json.loads(simpleworkspace.io.file.Read(filepath))

    def _ExportSettingsFile(self, settingsObject, outputPath):
        '''responsible for saving the settingsObject to file location in self._settingsPath'''
        jsonData = _json.dumps(settingsObject)
        simpleworkspace.io.file.Create(outputPath, jsonData)

    _cached_GetTypedSettingPropNames = None
    def _GetTypedSettingPropNames(self):
        '''returns dictionary of key = propertyNames of typedSettings, and the value consists of the settingName aka without "Setting_" prefix'''
        if(self._cached_GetTypedSettingPropNames is not None):
            return self._cached_GetTypedSettingPropNames
        
        allTypedProperties = {}
        classReflector = vars(self.__class__)
        for propertyName, value in classReflector.items():
            if (propertyName.startswith("Setting_")) and (not callable(value)):
                allTypedProperties[propertyName] = propertyName.removeprefix("Setting_")

        self._cached_GetTypedSettingPropNames = allTypedProperties
        return self._cached_GetTypedSettingPropNames

    def _MapTypedSettings(self, settingsObject: dict):
        '''Is an automapper by default for all Settings_xxx variables(Case Sensitive!), you may override this if you want to map specific logic'''
        allTypedProperties = self._GetTypedSettingPropNames()

        for key, value in settingsObject.items():
            propertyName = "Setting_" + key
            if (propertyName in allTypedProperties):
                setattr(self, propertyName, value)
        return
    
    def _ExportTypedSettings(self):
        '''Maps all the typed variables to settingsObject to prepare for exporting the file'''
        settingsObject = {}
        allTypedProperties = self._GetTypedSettingPropNames()
        for propertyName, settingName in allTypedProperties.items():
            settingsObject[settingName] = getattr(self, propertyName)
        return settingsObject

    def ClearSettings(self):
        self._MapTypedSettings(_deepcopy(self._cached_DefaultSettings))

    def LoadSettings(self):
        '''Loads the setting file from specified location to the memory at self.settings'''
        self.ClearSettings()
        if not (_os.path.exists(self._settingsPath)):
            return

        settingsObject = self._ParseSettingsFile(self._settingsPath)
        self._MapTypedSettings(settingsObject)
        return

    def SaveSettings(self):
        settingsObject = self._ExportTypedSettings()
        self._ExportSettingsFile(settingsObject, self._settingsPath)




# class SettingsManagerExample(SettingsManager_AutoMapped_JSON):
#     Setting_autorun = 1
#     Setting_testString = "hej"

# settingsManager = SettingsManagerExample("./test1.txt")
# settingsManager.LoadSettings()
# settingsManager.Setting_autorun = 5
# settingsManager.SaveSettings()
