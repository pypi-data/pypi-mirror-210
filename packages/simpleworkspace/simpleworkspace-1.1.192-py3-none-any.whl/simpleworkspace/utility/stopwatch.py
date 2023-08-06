import time as _time
from typing import Callable

class StopWatch:
    def __init__(self) -> None:
        self.timeHistory = []
        self.__timeElapsed = 0
        self.__isRunning = False

    def Start(self):
        if(self.__isRunning):
            return
        self.__isRunning = True
        self.timeHistory.append({
            "timestamp": _time.perf_counter(),
            "isStartEvent": True
        })
        self.__UpdateTimeElapsed()
        return
    
    def Stop(self):
        if not(self.__isRunning):
            return
        self.__isRunning = False
        self.timeHistory.append({
            "timestamp": _time.perf_counter(),
            "isStartEvent": False
        })
        return
    def Reset(self):
        '''Stops and resets the timer'''
        self.__init__()
        return

    def __UpdateTimeElapsed(self):
        endTime = _time.perf_counter() #take end time directly to avoid spending time while calculating
        self.__timeElapsed = 0
        startTime = None
        for timeEvent in self.timeHistory:
            if(timeEvent["isStartEvent"]):
                startTime = timeEvent["timestamp"]
                continue
            self.__timeElapsed += timeEvent["timestamp"] - startTime
            startTime = None
        if(startTime is not None):
            self.__timeElapsed += endTime - startTime

    def _PrecisionConverter(self, value:float|int, decimalPrecision:int):
        """
        Converts a value to the specified decimal precision.
        
        :param value: The value to be converted.
        :param decimalPrecision: The decimal precision.
            
        :Return: The converted value.
        """
        if(decimalPrecision < 1):
            decimalPrecision = None #None as decimalPrecision strips all decimals and returns int, but precision of even 0 returns a float 1.0
        return round(value, decimalPrecision) 

    def GetElapsedSeconds(self, decimalPrecision:int = None) -> float: 
        """
        Returns the elapsed time in seconds.
        
        :param decimalPrecision: The decimal precision of the returned time (default=None, which returns the maximum precision).
            
        :return: The elapsed time in seconds.
        """
        self.__UpdateTimeElapsed()
        timeElapsed = self.__timeElapsed
        if(decimalPrecision is not None):
            timeElapsed = self._PrecisionConverter(timeElapsed, decimalPrecision)
        return timeElapsed

    def GetElapsedMilliseconds(self, decimalPrecision:int = None):
        """
        Returns the elapsed time in milliseconds.
        
        :param decimalPrecision: The decimal precision of the returned time (default=None, which returns the maximum precision with no rounding).
            
        :return: The elapsed time in milliseconds.
        """
        
        timeElapsed = self.GetElapsedSeconds() * 1000
        if(decimalPrecision is not None):
            timeElapsed = self._PrecisionConverter(timeElapsed, decimalPrecision)
        return timeElapsed
    
    def ToString(self, decimalPrecision:int = None) -> str:
        """
        Returns a string representation of the elapsed time in seconds with high precision.

        :param decimalPrecision: The number of decimal places to round the elapsed time to. If None, no rounding is performed. Defaults to None.

        :return: A string representation of the elapsed time in seconds, rounded to the specified number of decimal places (if any).
        """

        return str(self.GetElapsedSeconds(decimalPrecision=decimalPrecision))
    
    def __enter__(self):
        self.Start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.Stop()
        return
    
    def __str__(self) -> str:
        return str(self.GetElapsedSeconds())
        
    


