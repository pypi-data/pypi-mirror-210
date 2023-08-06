import hashlib as _hashlib
import os as _os
import string
from typing import Callable as _Callable

class FileInfo:
    """
    Notes
    * all backslashes are replaced with forward ones for simplicity 
    * If no match can be found for any property, they will default to empty string
      
    """
    from functools import cached_property as _cached_property

    def __init__(self, filepath:str) -> None:
        self.rawPath = filepath.replace("\\", "/")
        '''the input path, example case: a/b/test.exe -> a/b/test.exe'''

    @_cached_property
    def IsDirectory(self) -> bool:
        return _os.path.isdir(self.rawPath)
    
    @_cached_property
    def IsFile(self) -> bool:
        return _os.path.isfile(self.rawPath)
    
    @_cached_property
    def IsSymlink(self) -> bool:
        return _os.path.islink(self.rawPath)
    
    @_cached_property
    def Exists(self) -> bool:
        return _os.path.exists(self.rawPath)

    @_cached_property
    def RealPath(self) -> str:
        '''converts the input path to an absolute path, example case: a/b/test.exe -> c:/a/b/test.exe'''
        return _os.path.realpath(self.rawPath).replace("\\", "/")

    @_cached_property
    def Tail(self) -> str:
        '''Retrieves everything before filename, example case: a/b/test.exe -> a/b'''

        tail, head = self._HeadTail
        return tail

    @_cached_property
    def Head(self) -> str:
        '''Retrieves everything after last slash which would be the filename or directory, example case: a/b/test.exe -> test.exe'''

        tail,head = self._HeadTail
        return head
    
    @_cached_property
    def Filename(self) -> str:
        '''retrieves filename without extension, example case: a/b/test.exe -> test'''

        return self._FilenameSplit[0]
    
    @_cached_property
    def FileExtension(self) -> str:
        '''retrieves fileextension without the dot, example case: a/b/test.exe -> exe'''

        if(len(self._FilenameSplit) == 2):
            return self._FilenameSplit[1]
        return ""
    
    @property
    def Parent(self) -> 'FileInfo':
        return FileInfo(self.Tail)

    @_cached_property
    def _HeadTail(self) -> tuple[str,str]:
        return _os.path.split(self.rawPath)
    
    @_cached_property
    def _FilenameSplit(self) -> str:
        return self.Head.rsplit(".", 1)
    
    @property
    def __str__(self) -> str:
        return self.rawPath




def Hash(filePath: str, hashFunc=_hashlib.sha256()) -> str:
    from simpleworkspace.types.byte import ByteEnum
    Read(filePath, lambda x: hashFunc.update(x), readSize=ByteEnum.MegaByte.value * 1, getBytes=True)
    return hashFunc.hexdigest()

def Read(filePath: str, callback: _Callable[[str | bytes], None] = None, readSize=-1, readLimit=-1, getBytes=False) -> (str | bytes | None):
    """
    :callback:
        the callback is triggered each time a file is read with the readSize, 
        callback recieves one parameter as bytes or str depending on getBytes param
    :readSize: amount of bytes to read at each callback, default of -1 reads all at once
    :ReadLimit: Max amount of bytes to read, default -1 reads until end of file
    :getBytes: specifies if the data returned is in string or bytes format
    :Returns
        if no callback is used, the filecontent will be returned\n
        otherwise None
    """
    from io import BytesIO, StringIO


    if (readSize == -1 and readLimit >= 0) or (readLimit < readSize and readLimit >= 0):
        readSize = readLimit

    content = BytesIO() if getBytes else StringIO()
    openMode = "rb" if getBytes else "r"
    totalRead = 0
    with open(filePath, openMode, newline=None) as fp:
        while True:
            if readLimit != -1 and totalRead >= readLimit:
                break
            data = fp.read(readSize)
            totalRead += readSize
            
            if not data:
                break

            if callback is None:
                content.write(data)
            else:
                callback(data)

    if callback is None:
        return content.getvalue()
    return None


    
def Create(filepath: str, data: bytes | str = None):
    if type(data) is str:
        data = data.encode()
    with open(filepath, "wb") as file:
        if data is not None:
            file.write(data)

def Append(filepath: str, data: bytes | str):
    if type(data) is bytes:
        pass  # all good
    elif type(data) is str:
        data = data.encode()
    else:
        raise Exception("Only bytes or string can be used to append to file")
    with open(filepath, "ab") as file:
        file.write(data)


def CleanInvalidNameChars(filename:str, allowedCharset = string.ascii_letters + string.digits + " .-_"):
    return ''.join(c for c in filename if c in allowedCharset)
