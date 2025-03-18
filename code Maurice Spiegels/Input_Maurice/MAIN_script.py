# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 10:55:09 2014

@authors: Maurice Spiegels, Gaby Kleijn
"""

import background_script as GET
import sys
import math
import time
import motion
from naoqi import ALProxy

motion = None
tts = None
trackface = None

    
video_data = GET.Vdata()
CONTINUE = True
initLEDs = 0
count = 0
state = 0

def printline(text, x=0):
    global EnablePytts
    """Print and wait for x seconds"""
    
    print str(text)
    time.sleep(x)
            
def angle(degrees):
    """ convert angle in degrees to radians"""
    radians = degrees*(math.pi/180)
    
    return radians
    
def NaoLEDs(naogaze, video_data):
    global initLEDs
    global leds
    global naoConn
    brightness = 0.5
    
    if naoConn:
        if initLEDs == 0:
            leds = ALProxy("ALLeds", naoIP, 9559)
            leds.setIntensity("BrainLeds", 0, 0)
            initLEDs = 1
            
        if initLEDs == 1:
            # Do something with the LEDs if you like (some example code below)
#            leds.setIntensity("LeftEarLeds", brightness, 0)
#            leds.setIntensity("RightEarLeds", brightness, 0) 
            pass


def NaoInitialize():
    global naoConn
    global motion
    global tts
    global trackface
    global Motionspeed
    
    if naoConn:              
        # Initialize and create Proxy's to be used
        try:
            motion = ALProxy("ALMotion", naoIP, 9559)
            tts = ALProxy("ALTextToSpeech", naoIP, 9559)
            trackface = ALProxy("ALFaceTracker", naoIP, 9559)
        
            tts.setLanguage("English")
            tts.setVolume(0.8)
            tts.say("\RSPD=115\ "+"\VCT=100\ "+"Lets start") #RSPD=Speed, VCT=Pitch (\RSPD=115\ "+"\VCT=85\)
            
            # enable stiffness only on head.
            motion.setStiffnesses("LArm", 1)
            motion.setStiffnesses("RArm", 1)
            motion.setStiffnesses("LLeg", 1)
            motion.setStiffnesses("RLeg", 1)
            motion.setStiffnesses("Head", 0.8) 
 
            # go to an init head pose.
            trackface.stopTracker()
            isAbsolute = True                      #Absolute False means relative to current position.
            motion.angleInterpolation("Head", [angle(0), angle(-5)], MotionSpeed, isAbsolute)         #this is a blocking function (cannot be interupted until finished)                                                                             #Absolute False means relative to current position.
            ## motion.angleInterpolationWithSpeed("HeadYaw", angle(65), 0.5)    #is also a blocking function
            ## motion.setAngles("HeadYaw", angle(65), 0.5)                      #is a NON-blocking function
            
        except Exception, e:
            print "Error was: ", e
            print "Could not create proxys, check if Nao connected"
            raw_input("Press CTRL+C followed by ENTER to exit, or ENTER to continue without Nao: ")
            naoConn = 0

def ManageFaceTracker(stoptracker = 0, MotionSpeed = None):
    global naoConn
    global trackface
    global startCount
    global speed
    global count
    
    if naoConn:
        if stoptracker == 1:
            trackface.stopTracker()
            startCount = time.clock()
            speed = MotionSpeed
            count = 1
        elif count == 1:
            if time.clock()-startCount >= speed:
               trackface.startTracker()
               count = 0
    
    return count
    
def TurnHeadNaoto(setHeadPos):
    global NaoHeadPos
    global naoConn
    global motion
    global MotionSpeed
    global tts
    global state

    if setHeadPos == 'L':
        ManageFaceTracker(1, MotionSpeed)
        Info = "*Nao turns head to the left"
        postureProxy = ALProxy("ALRobotPosture", naoIP, 9559)
        postureProxy.goToPosture("Stand", 0.5)
        motion.post.angleInterpolation("Head", [angle(0), angle(-30)], MotionSpeed, True) if naoConn else printline(Info, MotionSpeed/2.0)
        NaoHeadPos = 'L'

      
        
## ******************************************************************************************************************* ##
## ******************************************************************************************************************* ##
## ******************************************************************************************************************* ## 
"""
# Useful URLs for development of Nao code:
http://doc.aldebaran.com/2-1/naoqi/motion/control-walk.html
http://doc.aldebaran.com/2-1/naoqi/trackers/altracker.html
http://doc.aldebaran.com/2-1/naoqi/motion/control-joint-api.html#ALMotionProxy::getAngles__AL::ALValueCR.bCR
http://stackoverflow.com/questions/2601194/displaying-a-webcam-feed-using-opencv-and-python
"""

if __name__ == "__main__": 
#    naoIP = "169.254.59.24"
    naoIP = "192.168.0.114"
    naoConn = 1                     # 1 = Nao is connected, 0 = Nao is NOT connected
    MotionSpeed = 0.8               # The speed of the actuators with which the Nao performs movements
    iterSpeed = 0.3

    try:
        while CONTINUE:
            
            time.sleep(iterSpeed) if naoConn else time.sleep(iterSpeed)  #To limit maximum loop frequence if naoConn == 0
            video_data = GET.VideoData(naoIP, naoConn)
            ManageFaceTracker() # Always keeps the facetracker manager updated to automatically enable it again after x time.
            if video_data.KeyPressChar == "q":
                postureProxy = ALProxy("ALRobotPosture", naoIP, 9559)
                postureProxy.goToPosture("Crouch", 0.5)
                CONTINUE = False
                print "User terminating state-sequence script by key-press (q)"

            if state == 0:
                NaoInitialize()
                state = 1
            
            elif state == 1:
                info = ("Hello Gaybie")
                tts.say(info) if naoConn else printline(info, 1)
                TurnHeadNaoto('L')
#                trackface.startTracker()
                state = 2
            
            elif state == 2:
                print str(video_data)
                print video_data.facedetected
                #pass # Do something with the data from video_data

                
                if video_data.facedetected == True: 
                     
                    #print str(video_data)
                    #print video_data.facedetected
                    camera_facesize_1m = 75
                    AC = camera_facesize_1m/video_data.facesize
                    pitch = 35
                    alpha = pitch*math.pi/180
                    distance = math.cos(0.5*alpha)*AC
                    print distance


                   # postureProxy = ALProxy("ALRobotPosture", naoIP, 9559)
                    #postureProxy.goToPosture("StandInit", 0.5)
                    #X = 0.8
                    #Y = 0.0
                    #Theta = headpose[0]
                    #Frequency = 0.5 
                    #motionProxy.setWalkTargetVelocity(X, Y, Theta, Frequency)

                    
                pass # Do something with the data from video_data
            pass # Do something with the data from video_data


    except KeyboardInterrupt:
        print "User terminating state-sequence script"
        pass

    GET.VideoData(stop=1)
    motion.setStiffnesses("Body", 0) if naoConn else printline("Stiffness is disabled") 
