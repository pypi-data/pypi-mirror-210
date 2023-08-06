from typing import Callable as _Callable
import os as _os

def Create(path: str):
    '''Create all non existing directiores in specified path'''
    _os.makedirs(path, exist_ok=True)

def List(
        searchDir: str,
        callback: _Callable[[str], None] = None,
        includeDirs=True, includeFiles=True,
        includeFilter:str|_Callable[[str],bool]=None,
        satisfiedCondition: _Callable[[str], bool] = None,
        exceptionCallback: _Callable[[Exception], None] = None, #empty placeholder
        maxRecursionDepth: int=None
        ) -> (list[str] | None):
    """
    Recursively iterate all driectories in a path.
    All encountered exceptions are ignored

    :param callback: feeds full filepath to a callback
    :param includeFilter: Callback or Regex string
        * callback that takes the fullpath and returns true for paths that should be included
        * regex string which searches full path of each file, if anyone matches a callback is called. Example: "/mySearchCriteria/i"
    :param satisfiedCondition: takes a callback that returns a bool, if it returns true, no more search is performed
    :param exceptionCallback: run callback on any raised exception
    :param maxRecursionDepth: Specify how many levels down to list folders, level/depth 1 is basically searchDir entries

    :returns: a list of all found filepaths if no callback is given, otherwise None
    """
    from simpleworkspace.utility import regex

    if not _os.path.isdir(searchDir):
        raise NotADirectoryError(f'Supplied path is not a valid directory: "{searchDir}"')

    # only returned if callback was not given
    allEntries = [] if (callback is None) else None

    currentFolderDepth = 1 #this is basically the base directory depth with its entries and therefore the minimum value
    folderQueue = [searchDir]
    while (len(folderQueue) > 0):
        if (maxRecursionDepth is not None) and (currentFolderDepth > maxRecursionDepth):
            break
        currentFolderQueue = folderQueue
        folderQueue = []
        for currentFolder in currentFolderQueue:
            try:
                with _os.scandir(currentFolder) as entries:
                    for entry in entries:
                        filePath = entry.path

                        if(includeFilter is None):
                            pathMatchesIncludeFilter = True
                        elif(isinstance(includeFilter, str)):
                            pathMatchesIncludeFilter = regex.Match(includeFilter, filePath) is not None
                        else: #callback
                            pathMatchesIncludeFilter = includeFilter(filePath)

                        if entry.is_file():
                            if (includeFiles and pathMatchesIncludeFilter):
                                if callback is not None:
                                    callback(filePath)
                                else:
                                    allEntries.append(filePath)
                        elif(entry.is_dir()):
                            if (includeDirs and pathMatchesIncludeFilter):
                                if callback is not None:
                                    callback(filePath)
                                else:
                                    allEntries.append(filePath)
                            folderQueue.append(filePath)
                        else:
                            pass #skip symlinks
                        if satisfiedCondition is not None and satisfiedCondition(filePath):
                            return allEntries
            except (PermissionError, FileNotFoundError, NotADirectoryError) as ex: 
                #common raises that can safely be skipped!

                #PermissionError: not enough permission to browse folder, a common error when recursing unkown dirs, simply skip if no exception callback

                #FileNotFound or NotADirectory errors:
                #   since we know we had a valid path from beginning, this is most likely that a file or folder
                #   was removed/modified by another program during our search
                if(exceptionCallback is not None):
                    exceptionCallback(ex)
            except (OSError, InterruptedError, UnicodeError):
                #this one is tricker and might potentially be more important, eg a file can temporarily not be accessed being busy etc.
                #this is still a common exception when recursing very deep, so we don't act on it except for when exceptionCallback is provided

                #InterruptedError: Raised if the os.scandir() call is interrupted by a signal.
                #UnicodeError: Raised if there are any errors while decoding the file names returned by os.scandir().

                if(exceptionCallback is not None):
                    exceptionCallback(ex)
            except Exception as e:
                #here something totally unexpected has happened such as a bad callback supplied by user etc,
                #this one always raises exception even if exceptioncallback is not supplied

                #an completely invalid input supplied to os.scandir() such as empty string or a string not representing a directory
                #might raise TypeError and ValueError, we dont specifically handle these since we in these cases want to fully
                #raise an exception anyway

                if(exceptionCallback is None):
                    raise e
                else:
                    exceptionCallback(e)
        currentFolderDepth += 1

    return allEntries


def Remove(path: str) -> None:
    '''removes a whole directory tree'''
    import shutil
    shutil.rmtree(path, ignore_errors=True)
