import os, sys, glob, serial, time, datetime, threading
import serial.tools.list_ports
from colorama import init, Fore, Style
from threading import Thread, Timer
from functools import wraps 

def waiting(flag, function, interval = 0.1):    
    while not flag:
        rest(interval)             
    function()

def rest(secs = 1, interval=0.1, lapse = False):
    cnt = 60 * secs / 6
    while cnt > 0:
        time.sleep(interval)
        if lapse: print('.')
        cnt -= 1
          
class DuplicateThreadObjectError(Exception): pass
  
class RepeatingTimer(object):
    def __init__(self, timeout, eventfnc, daemon = False, *args, **kwargs):
        '''
        Description:
            Creating a new thread of Timer .
            eventfnc will be execute when time's up
        Remark:
            The interval the threading.Timer will wait before executing its action 
            may not be exactly the same 
            as the interval specified by the user.
        '''
        self.timeout    = timeout 
        self.eventfnc   = eventfnc
        self.args       = args
        self.kwargs     = kwargs
        self.timer      = None
        self.is_start   = False
        self.is_stop    = False
        self.daemon     = daemon
          
    def callback(self):
        self.eventfnc(*self.args, **self.kwargs)
        self.start()
  
    def clear(self):
        return self.cancel()
      
    def stop(self):
        return self.cancel()
  
    def cancel(self):
        with threading.Lock():
            if self.timer:
                # beyond 1000 error will thrown 
                # time.sleep(self.timeout/1000)
                self.timer.cancel()
                with threading.Lock():
                    while self.timer.isAlive(): # while isAlive() is True
                        time.sleep(1)
                    else:
                        self.is_stop    = True
            else:
                # ------ Never start == stopped
                self.is_stop    = True
        # Should be only returning self.is_stop = True
        return self.is_stop
  
    def start(self):
        try:
            self.timer = Timer(self.timeout, self.callback)
            self.timer.daemon = self.daemon
            self.timer.start()
            self.is_start = True  
        except Exception as e:
            raise DuplicateThreadObjectError("Exact same thread has started. \n %s" % e)