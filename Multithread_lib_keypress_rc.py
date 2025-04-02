#import getkey as gk #does not work probably because initialising each time
import get_keyboard as gk
import time

"""
@author: Maurice Spiegels

Up-arrow key     =   pitch + 0.2
Down-arrow key   =   pitch - 0.2
Right-arrow key  =   yaw + 0.2
Left-arrow key   =   yaw - 0.2
Numbers [1-9]    =   select option
Numpad +         =   set selected option as positive (preferred choice)
Numpad -         =   set selected option as negative (eliminate choice)
"""

#from multiprocessing import Process, Queue
from threading import Thread
from queue import Queue

KeyPress = ''
offset_pitch=0.0
offset_yaw=0.0
current_pitch = 0.0
current_roll = 0.0
current_yaw = 0.0

pKeyPress = None
cKey = gk.Key_Stroke()
qKey = Queue()

def GetKey():
    global KeyPress
    global offset_pitch, offset_yaw
    
    # # Needs opencv window to work
    # # k = cv2.waitKey(1)
    # if k == 2490368:        #Up-arrow key
    #     offset_pitch -= 0.2
    # elif k == 2621440:      #Down-arrow key
    #     offset_pitch += 0.2
    # elif k == 2555904:      #Right-arrow key
    #     offset_yaw -= 0.2
    # elif k == 2424832:      #Left-arrow key
    #     offset_yaw += 0.2
    # KeyPress = chr(k & 255)
    
    Keypress = gk.getkey()

    if KeyPress == 'up':        #Up-arrow key
        offset_pitch -= 0.2
    elif KeyPress == 'down':      #Down-arrow key
        offset_pitch += 0.2
    elif KeyPress == 'right':      #Right-arrow key
        offset_yaw -= 0.2
    elif KeyPress == 'left':      #Left-arrow key
        offset_yaw += 0.2
    
    #if KeyPress!='':
    print(KeyPress, offset_pitch, offset_yaw)
    return KeyPress

def RunGetKey(cKey, qKey):
    done = False
    while not done:
        if cKey.kbhit():
            c = cKey.getch()
            qKey.put(c)
            print('you pressed: ' + c + " , " + str(ord(c)))
            if c == 'q':
                done = True

            

    
    
    
def CreateProcesses():
    global pKeyPress, cKey, qKey
    if pKeyPress == None:      
        pKeyPress = Thread(target = RunGetKey, args=(cKey, qKey))
        pKeyPress.start()
    else:
        print('Keyboard process already running.')

def StopProcesses():
    global pKeyPress, cKey

    if pKeyPress !=None:
        pKeyPress.join()
        pKeyPress = None
        del cKey

    
if __name__=="__main__":
    CreateProcesses()
    time.sleep(10)
    done = False
    while not done:
        if not qKey.empty():
            c = qKey.get()
            qKey.task_done()
            print("Got "+ c + " from queue.")
        else:
            if c == 'q':
                qKey.join()
                done = True
    StopProcesses()