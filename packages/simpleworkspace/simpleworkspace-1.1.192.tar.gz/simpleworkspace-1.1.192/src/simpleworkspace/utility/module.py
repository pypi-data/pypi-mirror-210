import sys as _sys
import os as _os

def RequireModules(modules: list[str]) -> bool:
    '''
    Checks if python modules are installed, otherwise tries to install them
    '''
    import importlib
    import subprocess
    import pkg_resources
    
    required = modules
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed
    if missing:
        print("Please wait a moment, application is missing some modules. These will be installed automatically...")
        python = _sys.executable
        for i in missing:
            try:
                subprocess.check_call([python, "-m", "pip", "install", i])
            except Exception as e:
                pass
    importlib.reload(pkg_resources)
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed
    if missing:
        print("Not all required modules could automatically be installed!")
        print("Please install the modules below manually:")
        for i in missing:
            print("    -" + i)
        return False
    return True

def ImportModuleDynamically(moduleName, path):
    '''
    :param moduleName: freely name the module to import
    :param path: full path to the python module
    '''
    import importlib.util

    spec = importlib.util.spec_from_file_location(moduleName, path)
    mod = importlib.util.module_from_spec(spec)
    _sys.modules[moduleName] = mod
    _sys.path.append(_os.path.dirname(_os.path.abspath(path)))
    spec.loader.exec_module(mod)
    return mod

def ChangeCWDToMainModule():
    '''Set the directory of the main script module as the current working directory'''
    _os.chdir(ModuleInfo().Path_Directory)

class ModuleInfo:
    ''' A wrapper class for retrieving information about a module '''
    from functools import cached_property as _cached_property
    from typing import TypeVar

    _T = TypeVar('_T')

    def __init__(self, module=_sys.modules["__main__"]):
        '''
        :param module: The module to retrieve information from. Defaults to '__main__'.
        '''
        self.rawModule = module

    @_cached_property
    def Path_Absolute(self):
        '''
        Return the absolute path of the module.

        Example output:
        '/path/to/main_script.py'
        '''
        return _os.path.abspath(self.rawModule.__file__)
    
    @_cached_property
    def Path_Filename(self):
        '''
        Return the filename of the module.

        Example output:
        'main_script.py'
        '''
        return _os.path.basename(self.Path_Absolute)

    @_cached_property
    def Path_Directory(self):
        '''
        Return the directory of the module.

        Example output:
        '/path/to'
        '''
        return _os.path.dirname(self.Path_Absolute)

    def GetDeclaredClasses(self, targetClass: type[_T], includeChildsOnly=False) -> dict[str, type[_T]]:
        '''
        Get the classes declared in the module that are subclasses of the specified target class and the target class itself.

        :param targetClass: The target class to search for.
        :param includeChildsOnly: If True, include only child classes of the target class, aka exclude targetClass itself
        :return: A dictionary containing the matched class names as keys and class objects as values.
        '''
        import inspect

        matchedClasses = {}
        for className, classObj in inspect.getmembers(self.rawModule, inspect.isclass):
            if(not issubclass(classObj, targetClass)):
                continue
            if(includeChildsOnly and classObj == targetClass):
                continue
            if(self.rawModule.__name__ != classObj.__module__):
                continue

            matchedClasses[className] = classObj
        
        return matchedClasses