import logging as _logging
from simpleworkspace.types.byte import ByteEnum as _ByteEnum
import sys as _sys
import os as _os

class _BaseLogger:
    @staticmethod
    def DetailedFormatter(useUTCTime=True):
        import time
        '''style "<msPrecisionTime> <LevelName> <<ModuleName>, <LineNo>>: <Message>"'''
        if useUTCTime:
            formatter = _logging.Formatter(fmt="%(asctime)s.%(msecs)03d+0000 %(levelname)s <%(module)s,%(lineno)s>: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            formatter.converter = time.gmtime
        else:
            timeZoneStr = time.strftime("%z") # "+0200"
            formatter = _logging.Formatter(fmt="%(asctime)s.%(msecs)03d" + timeZoneStr + " %(levelname)s <%(module)s,%(lineno)s>: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        return formatter
    
    @staticmethod
    def BareMinimumFormatter():
        '''style "<LevelName>: <Message>"'''
        return _logging.Formatter(fmt="%(levelname)s: %(message)s")
    @staticmethod
    def RegisterAsUnhandledExceptionHandler(logger):
        def UncaughtExeceptionHandler(exc_type, exc_value, exc_traceback):
            if not issubclass(exc_type, KeyboardInterrupt): #avoid registering console aborts such as ctrl+c etc
                logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
            _logging.shutdown()
            _sys.__excepthook__(exc_type, exc_value, exc_traceback)

        _sys.excepthook = UncaughtExeceptionHandler
    


class RotatingFileLogger:

    @staticmethod
    def GetLogger(filepath, minimumLogLevel=_logging.DEBUG, maxBytes=_ByteEnum.MegaByte.value * 100, maxRotations=10, useUTCTime=True, registerGlobalUnhandledExceptions=False):
        from logging.handlers import RotatingFileHandler
        
        def rotator(source, dest):
            import gzip 
            with open(source, "rb") as sf:
                gzip_fp = gzip.open(dest, "wb")
                gzip_fp.writelines(sf)
                gzip_fp.close()
            _os.remove(source)

        logger = _logging.getLogger(f"__ROTATINGFILELOGGER_{hash((filepath,minimumLogLevel,maxBytes,maxRotations,useUTCTime))}")
        if(registerGlobalUnhandledExceptions):
            _BaseLogger.RegisterAsUnhandledExceptionHandler(logger)
        if(logger.hasHandlers()):
            return logger
        
        FileLogger._CreateParentFolders(filepath)

        logger.setLevel(minimumLogLevel)
        handler = RotatingFileHandler(filepath, maxBytes=maxBytes, backupCount=maxRotations, encoding='utf-8')
        handler.rotator = rotator
        handler.namer = lambda name: name + ".gz"
        handler.setFormatter(_BaseLogger.DetailedFormatter(useUTCTime=useUTCTime))
        logger.addHandler(handler)

        return logger


class FileLogger:
    @staticmethod
    def GetLogger(filepath, minimumLogLevel=_logging.DEBUG, useUTCTime=True, registerGlobalUnhandledExceptions=False):
        logger = _logging.getLogger("__FILELOGGER_" + str(hash(f"{filepath}{minimumLogLevel}{useUTCTime}")))
        if(registerGlobalUnhandledExceptions):
            _BaseLogger.RegisterAsUnhandledExceptionHandler(logger)
        if(logger.hasHandlers()):
            return logger
        
        FileLogger._CreateParentFolders(filepath)
        logger.setLevel(minimumLogLevel)
        handler = _logging.FileHandler(filepath, encoding='utf-8')
        handler.setFormatter(_BaseLogger.DetailedFormatter(useUTCTime=useUTCTime))
        logger.addHandler(handler)
        return logger
    
    @staticmethod
    def _CreateParentFolders(filepath:str):
        filepath = _os.path.realpath(filepath)
        directoryPath = _os.path.dirname(filepath)
        if(directoryPath in ("", "/")):
            return
        _os.makedirs(directoryPath, exist_ok=True)


class StdoutLogger:
    @staticmethod
    def GetLogger(minimumLogLevel=_logging.DEBUG, useUTCTime=False, registerGlobalUnhandledExceptions=False):
        stdoutLogger = _logging.getLogger("__STDOUTLOGGER__" + str(hash(f"{minimumLogLevel}{useUTCTime}")))
        if(registerGlobalUnhandledExceptions):
            _BaseLogger.RegisterAsUnhandledExceptionHandler(stdoutLogger)
        if(stdoutLogger.hasHandlers()):
            return stdoutLogger
        stdoutLogger.setLevel(minimumLogLevel)
        stdoutLogger.addHandler(StdoutLogger.CreateDetailedHandler(useUTCTime))
        return stdoutLogger
    
    @staticmethod
    def GetBasicLogger(minimumLogLevel=_logging.DEBUG, useUTCTime=False, registerGlobalUnhandledExceptions=False):
        '''Very basic stdout logger with "<LogLevel>: <Message>"'''
        stdoutLogger = _logging.getLogger("__BASICSTDOUTLOGGER__" + str(hash(f"{minimumLogLevel}{useUTCTime}")))
        if(registerGlobalUnhandledExceptions):
            _BaseLogger.RegisterAsUnhandledExceptionHandler(stdoutLogger)
        if(stdoutLogger.hasHandlers()):
            return stdoutLogger
        stdoutLogger.setLevel(minimumLogLevel)
        stdoutLogger.addHandler(StdoutLogger.CreateBasicHandler())
        return stdoutLogger
    
    @staticmethod
    def CreateBasicHandler():
        handler = _logging.StreamHandler(_sys.stdout)   
        handler.setFormatter(_BaseLogger.BareMinimumFormatter())
        return handler

    @staticmethod
    def CreateDetailedHandler(useUTCTime=False):
        handler = _logging.StreamHandler(_sys.stdout)   
        handler.setFormatter(_BaseLogger.DetailedFormatter(useUTCTime=useUTCTime))
        return handler


class DummyLogger:
    @staticmethod
    def GetLogger():
        dummyLogger = _logging.getLogger("@@BLACKHOLE@@")
        if(dummyLogger.hasHandlers()):
            return dummyLogger
        dummyLogger.addHandler(_logging.NullHandler())
        dummyLogger.propagate = False
        return dummyLogger

