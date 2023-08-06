class App:
    @classmethod
    def Setup(cls, appName:str, appCompany:str=None, extraIdentifier:str=None):
        '''
        :param extraIdentifier: used for creating a more unique apphash to identify this program, will be bundled with appName and appCompany
        '''

        import os
        import simpleworkspace.io.directory
        import simpleworkspace.io.path
        from simpleworkspace.logproviders import RotatingFileLogger
        from simpleworkspace.settingsproviders import SettingsManager_JSON

        cls.appName = appName
        cls.appCompany = appCompany
        cls.extraIdentifier = extraIdentifier

        cls.appTitle = cls.appName if cls.appCompany is None else f"{cls.appName} - {cls.appCompany}"
        '''example: "appname - appcompany"'''

        cls.appHash = hash((cls.appName, cls.appCompany, cls.extraIdentifier))
        '''appname + appcompany + extraidentifier hashed together, numeric hash'''
    
        cls.path_AppData = simpleworkspace.io.path.GetAppdataPath(appName, appCompany)
        ''''C:\\Users\\username\\AppData\\Roaming\\AppCompany\\AppName'''
        cls.path_AppData_Storage = os.path.join(cls.path_AppData, "storage")
        '''windows example: 'C:\\Users\\username\\AppData\\Roaming\\AppCompany\\AppName\\Storage'''
        simpleworkspace.io.directory.Create(cls.path_AppData_Storage) # creates parent folders aswell
        
        cls._path_LogFile = os.path.join(cls.path_AppData, "App.log")
        cls.logger = RotatingFileLogger.GetLogger(cls._path_LogFile, registerGlobalUnhandledExceptions=True)

        cls._path_AppSettingsFile = os.path.join(cls.path_AppData, "AppConfig.json")
        cls.settingsManager = SettingsManager_JSON(os.path.join(cls.path_AppData, "AppConfig.json"))
        cls.settingsManager.LoadSettings()

