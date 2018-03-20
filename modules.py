"""
Standard modules that can be compatible for other projects
"""
import os, sys

DEBUG = False 

def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

def checkOS(win_var=None, linux_var=None):
    _var = None
    if win_var and linux_var:
        if sys.platform.startswith("win"):
            # print("Windows platform detected")
            _var = win_var
        elif sys.platform.startswith("linux"):
            # print("Linux platform detected")
            _var = linux_var
        else:
            raise EnvironmentError("Unsupported platform")
    else:
        print('Please provide at least 2 variables [windows_variable, linux_variable]')
    return _var   

class callbackEvent(object):
    def __init__(self, **kwargs):
        self.handlers   = []
        self._param     = None
        return super().__init__(**kwargs)
    
    def add(self, handler): 
        self.handlers.append(handler)
        if DEBUG: print('Callback event added')
        return self
    
    def addFunction(self, handler):
        self.add(handler)
    
    def param(self, _param):
        self._param     = _param
    
    def addParameter(self, _param):
        self.param(_param)
    
    def remove(self, handler):
        self.handlers.remove(handler)
        return self
    
    def clear(self):
        self.handlers   =[]
        self._param     = None
        if DEBUG: print('Callback event cleared')
         
    def empty(self):
        self.clear()
     
    def fire(self, var, *args, **earg):
        '''
        For now dont put the callback function as a part of a class with self
        '''
        for handler in self.handlers:
            handler(var, args, earg)
        if DEBUG: print('Callback event executed')
            
    def call(self, _var=None):
        if _var :   var = _var
        else:       var = self._param
        self.fire(var)
        self.clear()
        
    def callOCR(self, np_raw, np_data, rename):
        fnc = self._param
        for handler in self.handlers:
            handler(fnc, np_raw, np_data, rename)
        if DEBUG: print('OCR Callback event executed')
        self.clear()
            
    __iadd__ = add
    __isub__ = remove
    __call__ = fire