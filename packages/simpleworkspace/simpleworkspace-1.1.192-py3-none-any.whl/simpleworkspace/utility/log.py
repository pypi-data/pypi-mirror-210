from typing import Callable as _Callable
import os as _os
class RotatingLogReader:
    def __init__(self, logPath: str):
        """
        :param logPath: the full path to a live log, such as /var/log/apache/access.log,
            The parser handles already rotated files behind the scenes
        """

        self.logPath = _os.path.realpath(logPath)
        self.logFileName = _os.path.basename(self.logPath)
        self.logBaseDirectory = _os.path.dirname(self.logPath)
        self._internalBuffer = None

    def ToString(self):
        """
        :returns: All logs dumped to a string
        """
        from io import StringIO

        strBuilder = StringIO()
        def writeFunc(line:str):
            strBuilder.write(line)
            return False
        self.Read(writeFunc)
        return strBuilder.getvalue()

    def ToFile(self, outputPath):
        """
        Dumps all logs as one file
        """


        with open(outputPath, "w") as fp:
            def writeFunc(line: str):
                fp.write(line)
                return False
            self.Read(writeFunc)
        return

    def GetRelatedLogFilePaths(self) -> list[str]:
        """
        :returns: list of paths to the log itself + all of its rotated files, sorted newest to oldest logs example [log.txt, log.txt.1, log.txt.2.gz]
        """
        import re
        import simpleworkspace.io.directory
        import simpleworkspace.utility.regex

        logFiles = {}
        def logFilesFiltering(path: str):
            currentLogname = _os.path.basename(path)
            if(self.logFileName not in currentLogname):
                return
            if(self.logFileName == currentLogname):
                logFiles[0] = path
                return
            escLogName = re.escape(self.logFileName)
            match = simpleworkspace.utility.regex.Match(f"/^{escLogName}\.(\d+)/", currentLogname)[0]
            logFiles[int(match[1])] = path
            return
        simpleworkspace.io.directory.List(self.logBaseDirectory, callback=logFilesFiltering, includeDirs=False, maxRecursionDepth=1)

        sortedLogFiles = []
        sortedKeyList = sorted(logFiles.keys())
        for i in sortedKeyList:
            sortedLogFiles.append(logFiles[i])

        return sortedLogFiles

    def Read(self, satisfiedCondition: _Callable[[str], bool]):
        """
        :param satisfiedCondition: recieves log line as param, return true to stop reading further
        """
        import gzip

        oldestToNewestLogs = self.GetRelatedLogFilePaths()
        oldestToNewestLogs.reverse()

        for logPath in oldestToNewestLogs:
            fp = None
            if(logPath.endswith(".gz")):
                fp = gzip.open(logPath, "rt")
            else:
                fp = open(logPath, "r")
            
            for line in fp:
                if satisfiedCondition(line):
                    break

            fp.close()
        return
    