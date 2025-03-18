import cv2

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

from multiprocessing import Process, Queue

KeyPress = 0
offset_pitch=0.0
offset_yaw=0.0
current_pitch = 0.0
current_roll = 0.0
current_yaw = 0.0

pKeyPress = None

def GetKey():
    global KeyPress

    k = cv2.waitKey(1)
    if k == 2490368:        #Up-arrow key
        offset_pitch -= 0.2
    elif k == 2621440:      #Down-arrow key
        offset_pitch += 0.2
    elif k == 2555904:      #Right-arrow key
        offset_yaw -= 0.2
    elif k == 2424832:      #Left-arrow key
        offset_yaw += 0.2
    KeyPress = chr(k & 255)
    return KeyPress

def CreateProcesses():
    global pKeyPress

    pKeyPress = Process(target = GetKey, args=())
    pKeyPress.start()

def StopProcesses():
    global pKeyPress

    if pKeyPress !=None:
        pKeyPress.join()

    
        
