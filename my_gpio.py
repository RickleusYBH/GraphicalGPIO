from .modules           import callbackEvent
from .Timer_collections import rest
import RPi.GPIO as GPIO
import time, threading
from PyQt5              import QtCore
from PyQt5.Qt           import QObject
from PyQt5.QtCore       import pyqtSignal  

NAME_SCRIPT = '[GPIO]'
TEST_MODE = True

class Synthetic():        
    class __FlagCheck__(QtCore.QObject):
        '''The Boolean State Tracker'''
        isChanged     = QtCore.pyqtSignal()
        def __init__(self, default_flag):
            QObject.__init__(self)
            self.default_flag = default_flag                                        # Default False                             
        # API
        def isToggled(self, new_flag):
            if new_flag is not self.default_flag:   self.isChanged.emit()    
                
    class Button(object):     
        '''To simulate signal of pyqt button emitted and perform event callback'''      
        def __init__(self, *args):
            self.__qthread_check    = Synthetic.__FlagCheck__(False)                  # declare object 
            self.__qthread_check.isChanged.connect(self.__callback_GPIOThread)      # Connect custom pyqtsignal changes                
            self.__callbackThread   = callbackEvent()                                 # declare object
            self.__args             = args 
        def __callback_GPIOThread(self):
            self.__callbackThread.call(self)                                            # Perform event callback
        # API
        def isClicked(self, channel = None):
            self.__qthread_check.isToggled(True)                                    # Button is pressed
        # API
        def addButtonEvent(self, global_event):
            self.__callbackThread.add(global_event)                                 # declare callback for workerThread
            self.__callbackThread.param(self.__args)  

'''
Do not disable warnings unless under test mode
'''
GPIO.setwarnings(True)

class GPIOError(Exception)          : pass
class EventNotFoundError(Exception) : pass

GPIO_IN     = 'input'
GPIO_OUT    = 'output'

class GPIO_service(object):
    def __init__(self, input_pin=None, sender = '[???]', type=GPIO_IN):
        print('%s Set up GPIO %d into %s pin.' % (sender, input_pin, type))
        self.GPIO   = None
        self.DEBUG  = False
        if input_pin:
            self.PINOUT = input_pin    
            self.GPIO   = GPIO    
            self.GPIO.setmode(GPIO.BCM)                 # Setting configuration according to Pi Board physical layout
            
            if type == 'input':     self.GPIO.setup(self.PINOUT, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            elif type == 'output':  self.GPIO.setup(self.PINOUT, GPIO.OUT)
            else:                   raise GPIOError('GPIO Setup Failed. Please define pin as input/output')
            print('')     
            if TEST_MODE: print ('[GPIO] : %s ' % threading.current_thread().name)  
            print('Configured %s %d as %s pin.' % (NAME_SCRIPT, self.PINOUT, type))  
            print('')             
            self._reset_Event()
        else:
            raise GPIOError('GPIO Setup Failed. Input pin not found')
        
         
        
    def _reset_Event(self):
        self.oneClickEvent  = None
        self.isClickable    = True

    # Raw layer API            
    def add_event_detect(self, cb_event, _bouncetime = 100):
        self.GPIO.add_event_detect(self.PINOUT, self.GPIO.BOTH, callback = cb_event, bouncetime = _bouncetime)
        
    # Raw layer API        
    def add_falling_event_detect(self, cb_event, _bouncetime = 100):
        self.GPIO.add_event_detect(self.PINOUT, self.GPIO.FALLING, callback = cb_event, bouncetime = _bouncetime)
    
    # Raw layer API    
    def add_rising_event_detect(self, cb_event, _bouncetime = 100):
        self.GPIO.add_event_detect(self.PINOUT, self.GPIO.RISING, callback = cb_event, bouncetime = _bouncetime)
        
    def _remove_event_detect(self, _pin=None):
        if _pin:    pin = _pin
        else:       pin = self.PINOUT
        self.GPIO.remove_event_detect(pin)        
        if TEST_MODE: print('GPIO %d Callback event removed.' % pin)
        
    def _clean_up(self, _pin=None):
        '''
        As the software is not shutdown after boot up
        This function is practically unnecessary 
        '''
        if _pin:    pin = _pin
        else:       pin = self.PINOUT
        self.GPIO.cleanup(pin)
        if TEST_MODE: print('GPIO object removed.')
        
    def _clean_up_all(self):
        '''
        As the software is not shutdown after boot up
        This function is practically unnecessary 
        '''
        self.GPIO.cleanup()
        if TEST_MODE: print('All GPIO objects removed.')
        
    # Raw layer API   
    def remove_event_detect(self, pin=None):
        self._remove_event_detect(pin)     
        self._reset_Event()
    
    # API
    def isClicked(self, channel=None):
        self.remove_event_detect(channel)
        
    # API    
    def read(self): 
        if TEST_MODE : print('Reading GPIO %d current state.' % self.PINOUT)
        return (self.GPIO.input(self.PINOUT))
    
    # API    
    def write(self, state):
        if TEST_MODE : print('Setting GPIO %d to %s state.' % (self.PINOUT, state))
        self.GPIO.output(self.PINOUT, state)
    
    # API    
    def close(self):
        self.isClicked()

    # API    
    def exit(self):    
        self._clean_up()
        
    # API
    def assignButtonClickEvent(self, cb_event = None, _bouncetime = 100):
        if cb_event:
            self.oneClickEvent  = cb_event
            self._GUI_Button    = Synthetic.Button(self.PINOUT) 
            self.add_falling_event_detect(self._GUI_Button.isClicked, _bouncetime)             
            self._GUI_Button.addButtonEvent(self.oneClickEvent)                          # Add in the global callback           
        else: EventNotFoundError('Assign event')
        
class PulseGenerator(GPIO_service):
    def __init__(self,input_pin=None, sender = '[???]', type=GPIO_IN):
        GPIO_service.__init__(self, input_pin, sender, type)
        
    def setup(self):
        print('Auto Pulse Generator Activated.')
        
    def _stage_toggle_L2H(self, interval=0.5, cycle=None):
        self.GPIO.output(self.PINOUT, False)
        if self.DEBUG: print('0')
        time.sleep(interval)
        self.GPIO.output(self.PINOUT, True)
        if self.DEBUG: print('1')
        if cycle:   time.sleep(cycle-interval)
        else:       time.sleep(1-interval)
        
    def _stage_toggle_H2L(self, interval=0.5, cycle=None):
        self.GPIO.output(self.PINOUT, True)
        if self.DEBUG: print('1')
        time.sleep(interval)
        self.GPIO.output(self.PINOUT, False)
        if self.DEBUG: print('0')
        if cycle:   time.sleep(cycle-interval)
        else:       time.sleep(1-interval)

    # API        
    def stage_toggle_L2H(self, counter=None, time_stage = 0, interval=0.5, cycle=None, callback=None):
        if counter:
            while counter > 0:
                self._stage_toggle_L2H(interval, cycle)
                counter -= 1
                rest(time_stage)
        else:
            while True:
                self._stage_toggle_L2H(interval, cycle)
        if callback:    callback() 

    # API                
    def stage_toggle_H2L(self, counter=None, time_stage = 0, interval=0.5, cycle=None, callback=None):
        if counter:
            while counter > 0:
                self._stage_toggle_H2L(interval, cycle)
                counter -= 1
                rest(time_stage)
        else:
            while True:
                self._stage_toggle_H2L(interval, cycle) 
        if callback:    callback()