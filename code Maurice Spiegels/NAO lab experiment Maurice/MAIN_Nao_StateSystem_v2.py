# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 10:55:09 2014

@author: Maurice Spiegels
"""

import Multi_SUBprocess_v5 as SUB
from UtterancesForNao_v2 import GetDialogProgress, setUtteranceVARs, utterance, PREFIX
import sys
import math
import time
import pyttsx
import re
import itertools
from naoqi import ALProxy

motion = None
tts = None
trackface = None
    
EnablePytts = 1
pytts = pyttsx.init()
pytts.setProperty('rate', 150)
def PyttsSay(string=''):    
    pytts.say(str(string))
    pytts.runAndWait()
    
AVInput = SUB.AVdata()
AVold = SUB.AVdata()
LtsRtsTio_OLD = SUB.MIC.DialogStats()
LtsRtsTio_OLD = LtsRtsTio_OLD.LtsRtsTio
Lturns = AVInput.dialogdata.LturnCount
Rturns = AVInput.dialogdata.RturnCount
NameLeft = "PersonLEFT"
NameRight = "PersonRIGHT"
TTdelay = ''
utterance_text = ''
utterance_text_OLD = ''
PreSilenceCutInDetected = ''
GazeBeforeS_SilenceBeforeG = ''
select = itertools.cycle([1,0]).next
 
prev_state = 0
prev_turnSkipped = 0 
initRST = False
state = 0 # = NextState 
reset = 0
count = 0
Ssignal = False
TakeTurn = 0
NaoCalgaze = None
deviation = {'L':0, 'R':0}
NaoHeadPos = '-'
WindowisActive = False
GazeBeforeSilence = False
GazeBeforeXDelay = False
SilenceBeforeGaze = False
PreSilence = False
CutInDetected = False
staircase = ['?']*4
stepsize = None
maxStepsize = None
minStepsize = None
maxAdaptDelay = None
minAdaptDelay = None
TurnsSkipped = 0
CONTINUE = True
pauzed = '_'

firstrun = True
initLEDs = 0
initA = 0
initB = 0
initC = 0
initE = 0
initF = 0
initG = 0
initH = 0

def functionsRESET(n_state, n_turnSkipped):
    global initA
    global initB
    global initC
    global initE
    global initF
    global initG
    global initH
    
    global prev_state
    global prev_turnSkipped
    global initRST
    
    if n_state != prev_state:
        initRST = True
        prev_state = n_state
    
    if n_turnSkipped != prev_turnSkipped:
        initRST = True
        prev_turnSkipped = n_turnSkipped
    
    if initRST:
        print "STATE TRANSITION / TURN-SKIP TOOK PLACE --> RESET FUNCTIONS"
        initA = 0
        initB = 0
        initC = 0
        initE = 0
        initF = 0
        initG = 0
        initH = 0
        initRST = False
    else:
        pass
    
def TrueForXSeconds(WINsize = 2.0):
    global WindowisActive
    global WINstart
    
    now = time.clock()
    if WindowisActive == False:
        WindowisActive = True
        WINstart = now
    else:
        if now-WINstart > WINsize:
           WindowisActive = False
    
    return WindowisActive
    
#def silentforMAX(sec, AVInput, limit=60):
#    global initH
#    global t_1
#    global t_2
#    t_diff = 0
#    signal = False
#    if AVInput.mic != "-":
#        if initH == 0 and AVInput.mic == ".":
#            time_c = time.clock()
#            t_1 = time_c
#            t_2 = time_c
#            initH = 1
#            
#        elif initH == 1 and AVInput.mic == ".":
#            t_2 = time.clock()
#            t_diff = t_2-t_1
#        else:
#            time_c = time.clock()
#            t_1 = time_c
#            t_2 = time_c
#            
#        if initH == 1 and limit > t_diff >= sec-MeanSystemDelay:
#            signal = True
#            initH = 0  
#            
#    return signal
    
def silentfor(AVInput, sec=0):
    global initA
    global t1
    global t2
    
    signal = False
    if AVInput.mic != "-":   
        if initA == 0 and AVInput.mic == ".":
            time_c = time.clock()
            t1 = time_c
            t2 = time_c
            initA = 1
            
        elif initA == 1 and AVInput.mic == ".":
            t2 = time.clock()

        else:
            time_c = time.clock()
            t1 = time_c
            t2 = time_c
            #print "sound faaal"
            
        t_diff = t2-t1    
        
        if initA == 1 and t_diff >= sec-MeanSystemDelay:
            signal = True
            #initA = 0 
            #print "t_diff WINNAAAR =", t_diff
        else:
            signal = False
        
        #print "t_diff, signal =", t_diff, signal
    return signal

def someonespeaksfor(sec, AVInput):
    global initE
    global tx
    global ty
    t_diff = 0
    
    signal = False 
    if AVInput.mic != "-":
        if initE == 0 and AVInput.mic != ".":
            time_c = time.clock()
            tx = time_c
            ty = time_c
            initE = 1
            
        elif initE == 1 and AVInput.mic != ".":
            ty = time.clock()
            t_diff = ty-tx
        else:
            tx = time.clock()
            
        if initE == 1 and t_diff >= sec-MeanSystemDelay:
            signal = True
            initE = 0
               
    return signal
    
#def otherspeaksfor(sec, AVInput, naogaze):
#    global initB
#    global ta
#    global tb
#    t_diff = 0
#    
#    signal = False 
#    if AVInput.mic != "-":  
#        
#        if initB == 0 and AVInput.mic != "." and AVInput.mic != naogaze:
#            time_c = time.clock()
#            ta = time_c
#            tb = time_c
#            initB = 1
#        
#        elif initB == 1 and AVInput.mic != "." and AVInput.mic != naogaze:
#            tb = time.clock()
#            t_diff = tb-ta
#        else:
#            ta = time.clock()
#            
#        if initB == 1 and t_diff >= sec-MeanSystemDelay:
#            signal = True
#            initB = 0
#               
#    return signal

def otherspeaksfor(sec, AVInput, naogaze):
    global initB
    global ta
    global tb
    t_diff = 0
    
    signal = False 
    if AVInput.mic != "-":  
        
        if initB == 0 or AVInput.mic == naogaze or AVInput.mic == "B" or AVInput.mic == ".":
            time_c = time.clock()
            ta = time_c
            tb = time_c
            initB = 1
        
        elif initB == 1:
            tb = time.clock()
            
        t_diff = tb-ta
        
        if initB == 1 and t_diff >= sec-MeanSystemDelay:
            signal = True
            initB = 0
               
    return signal
    
def AdaptiveDelayPassed():
    global Cond2_adaptTTDelay
    global initG
    global Ts
    global Te
    t_diff = 0
    
    signal = False
    
    if initG == 0:
        time_c = time.clock()
        Ts = time_c
        Te = time_c
        initG = 1  
        
    elif initG == 1:
        Te = time.clock()
    
    t_diff = Te-Ts
        
    if initG == 1 and t_diff >= Cond2_adaptTTDelay-MeanSystemDelay:
        signal = True
        initG = 0
    
    return signal
      
def SameSpeakerfor(sec, AVInput):
    global initC
    global OLDspeaker
    global ts
    global te
    t_diff = 0
    
    signal = False
    if AVInput.mic != "-":
        
        if initC == 0 and AVInput.mic != ("." or "B"):
            OLDspeaker = AVInput.mic  #OLD speaker is either left or right
            time_c = time.clock()
            ts = time_c
            te = time_c
            initC = 1
        
        elif initC == 1 and AVInput.mic != ".":
            if AVInput.mic == (OLDspeaker or "B"):
                te = time.clock()
                t_diff = te-ts
            else:
                OLDspeaker = AVInput.mic
                ts = time.clock()
        else:
            ts = time.clock() # AVInput == '.' (i.e. silence)
            
        if initC == 1 and t_diff >= sec-MeanSystemDelay:
            signal = True
            initC = 0
                
    return signal    

def GazeToNaofor(sec, TrueGaze, AVInput):
    global initF
    global gs
    global ge
    global gazetol
    t_diff = 0
    
    signal = False
    if initF == 0 and -gazetol < TrueGaze < gazetol and AVInput.facedetected == True:
        time_c = time.clock()
        gs = time_c
        ge = time_c
        initF = 1
    
    elif initF == 1 and -gazetol < TrueGaze < gazetol and AVInput.facedetected == True:
        ge = time.clock()
        t_diff = ge-gs
    else:
        gs = time.clock() # Nao is not gazed upon anymore
        
    if initF == 1 and t_diff >= sec-MeanSystemDelay:
        signal = True
        initF = 0
                
    return signal
    
def TrueGaze(naogaze, AVnew, rst=False): # rst=1 manually re-initiates a head-pose calibration for either L or R
    global firstrun
    global calibrationLdone
    global calibrationRdone
    global deviation
    global AVold
    global AVInput
    global iteration
    global gazetol
    global output
    global DiffPerc
    
    reset = rst
    maxiter = 30    # The number of samples that are used to calibrate the Headpose Yaw (default = 40)
    maxreset = 5    # The number of retries before an error 'None' output is returned instead of 0.
    tolerance = gazetol-3.0   # Calibration requires more narrow limits compared to normal operation mode
    resetNR = 0
    
    
    if firstrun == True:
        deviation = {'L':0, 'R':0}
        calibrationLdone = False
        calibrationRdone = False           
        iteration = 0   
        reset = True
        firstrun = False
        output = None
    
    while reset == True:
        try:  
            AVInput = SUB.GetAVInput(naoIP, naoConn)
            AVold = AVInput
            if naogaze == 'L':
                deviation['L'] = 0
                calibrationLdone = False
            elif naogaze == 'R':
                deviation['R'] = 0
                calibrationRdone = False
            else:
                deviation['L'] = 0
                deviation['R'] = 0
                calibrationLdone = False
                calibrationRdone = False 
                print "Naogaze =", naogaze
                raw_input("Getting calibrated gaze failed, check naogaze input for validity. [press ENTER to continue]")          
            iteration = 0
            reset = False       
        except:
            if iteration<(maxiter*4):
                iteration += 1
                time.sleep(1.0/maxiter)
            else:
                print "AVInput =", naogaze
                raw_input("Getting calibrated gaze failed, check AVInput for validity. [press ENTER to continue]")                
                iteration = 0                
                output = None
                break
   
    if (reset == False and 
       ((naogaze == 'L' and calibrationLdone == False) or (naogaze == 'R' and calibrationRdone == False))):
            
        while iteration<maxiter:
            
            time.sleep(1.0/maxiter)
            AVInput = SUB.GetAVInput(naoIP, naoConn)

            if AVInput.headpose != AVold.headpose: # New == Old is extremely rare unless 'New' is not a true new sample.

                if iteration == 0:
                    sys.stdout.write("(re-)starting gaze calibration")
                    deviation[naogaze] = AVInput.headposeYaw
                    iteration = 1
                    
                else:
                    sys.stdout.write(".")
                    ValidFace = False
                    if (AVInput.facedetected and  # Several requirements to ensure proper calibration
                        AVold.facecenterX*(1-DiffPerc) < AVInput.facecenterX < AVold.facecenterX*(1+DiffPerc) and
                        AVold.facecenterY*(1-DiffPerc) < AVInput.facecenterY < AVold.facecenterY*(1+DiffPerc) and
                        AVold.facesize*(1-DiffPerc) < AVInput.facesize < AVold.facesize*(1+DiffPerc) and
                        AVInput.facesize > 80): # the dimensions must be at least 100 pixels
                            ValidFace = True
                        
                    if ((deviation[naogaze]-tolerance < AVInput.headposeYaw < deviation[naogaze]+tolerance) and 
                        ValidFace == True):
                        deviation[naogaze] = (deviation[naogaze]+AVInput.headposeYaw)*0.5
                        iteration += 1
                        
                    else:
                        if resetNR <= maxreset:
                            iteration = 1
                            resetNR += 1
                        else:
                            iteration = 0
                            resetNR = 0
                            output = None
                            break
              
                AVold = AVInput
        
        if iteration==maxiter:
            
            if naogaze == 'L':
                calibrationLdone = True
            elif naogaze == 'R':
                calibrationRdone = True
                
            iteration = 0
            print "\nDeviation %s =" %(naogaze), deviation[naogaze]
    
    if (naogaze == 'L' and calibrationLdone) or (naogaze == 'R' and calibrationRdone):
        output = round(AVnew.headposeYaw-deviation[naogaze],1)
    else:
        output = None
    
    return output

def SpeechLRorB(AVInput):
    return AVInput.mic
            
def angle(degrees):
    """ convert angle in degrees to radians"""
    radians = degrees*(math.pi/180)
    
    return radians

def LookingAtNao(naogaze, AVInput):
    global gazetol
    
    Bool = -gazetol<TrueGaze(naogaze, AVInput)<gazetol
    
    return Bool
    
def NaoLEDs(naogaze, AVInput):
    global initLEDs
    global leds
    global gazetol
    global naoConn
    brightness = 0.5
    
    if naoConn:
        if initLEDs == 0:
            leds = ALProxy("ALLeds", naoIP, 9559)
            leds.setIntensity("BrainLeds", 0, 0)
            initLEDs = 1
            
        if initLEDs == 1:
            try:
                if AVInput.mic == 'L': 
                    leds.setIntensity("LeftEarLeds", brightness, 0)
                    leds.setIntensity("RightEarLeds", 0, 0) 
                elif AVInput.mic == 'R': 
                    leds.setIntensity("LeftEarLeds", 0, 0)
                    leds.setIntensity("RightEarLeds", brightness, 0) 
                elif AVInput.mic == 'B': 
                    leds.setIntensity("LeftEarLeds", brightness, 0)
                    leds.setIntensity("RightEarLeds", brightness, 0) 
                else:
                    leds.setIntensity("LeftEarLeds", 0, 0)
                    leds.setIntensity("RightEarLeds", 0, 0)
                
                if LookingAtNao(naogaze, AVInput):
                    leds.setIntensity("BrainLedsFront", 1, 0)
                else:
                    leds.setIntensity("BrainLedsFront", 0, 0)
            except:
                pass

def wordslisttostr(listobj):
    if listobj != None:
        string = str(listobj)
        string = string.replace("['", "")
        string = string.replace("']", "")
        string = string.replace("', '", " ")
    else:
        string = ''
    return string
    
def UpdateLog(CreateHeader=False, CloseLog=False):
    global logfile
    global AVInput
    global AVold     
    global utterance_text
    global utterance_text_OLD
    global PreSilenceCutInDetected
    global GazeBeforeS_SilenceBeforeG
    global LtsRtsTio_OLD
    global GazeBeforeSilence
    global SilenceBeforeGaze
    global PreSilence
    global CutInDetected
    global TakeTurn
    global state
    global NaoCalgaze
    global TTwin
    global TTdelay
    global Cond1_fixedTTdelay
    global Cond2_adaptTTDelay
    global CONTINUE
    
    if CreateHeader == True:
        logfile = open(str(SessionID)+".csv", "w") # Will write app. 1.1Mb for very 15 minutes of runtime (f=20Hz)
        logfile.write(  'User_Id:,'+str(SessionID)+'\n'+
                        'Experiment_Condition:,'+str(ExpCond)+'\n'+
                        'TurnTake_Window_(s):,'+str(TTwin)+'\n'+
                        'Timestamp_(s),Iteration,MicInput,FaceDetected,Calibrated_yaw,TTSwords,NAO_Utterance,'+
                        'Nao_gaze_direction,Current_state,Dialog_phase,'+
                        'TakeTurn,GazeBeforeS;SilenceBeforeG,PreSilence;CutInDetected,Fixed/Adaptive_Delay,'+
                        'Left_turn_(s),Left_silence_(s),Right_turn_(s),Right_silence_(s),Turn_interval_(s),Turn_overlap_(s)'+'\n')
    
    else:
        if (AVold != AVInput and AVInput.iter != '-') or TakeTurn !=0:
            if utterance_text != utterance_text_OLD:
                NAO_txt = utterance_text.replace(',',';')
                utterance_text_OLD = utterance_text
            else:
                NAO_txt = ''
            if AVold.STTwords != AVInput.STTwords:
                STT_txt = wordslisttostr(AVInput.STTwords)
            else:
                STT_txt = ''
                
            if ExpCond == 1:
                TTdelay = Cond1_fixedTTdelay
                
                if TakeTurn == 1:
                    GazeBeforeS_SilenceBeforeG = str(GazeBeforeSilence)+';'+str(SilenceBeforeGaze)
                    PreSilenceCutInDetected = '_;'+str(CutInDetected)
                else:
                    GazeBeforeS_SilenceBeforeG = ''
                    PreSilenceCutInDetected = ''
                    
            elif ExpCond == 2:
                TTdelay = Cond2_adaptTTDelay
                GazeBeforeS_SilenceBeforeG = ''
                
                if TakeTurn == 1:
                    PreSilenceCutInDetected = str(PreSilence)+';'+str(CutInDetected)
                else:
                    PreSilenceCutInDetected = ''
                    
            elif ExpCond == 3:
                TTdelay = '0.140'
                GazeBeforeS_SilenceBeforeG = ''
                
                if TakeTurn == 1:
                    PreSilenceCutInDetected = '_;'+str(CutInDetected)
                else:
                    PreSilenceCutInDetected = ''
                
            DialogPhase = GetDialogProgress()
            now = round(time.clock(),2)    
            
            if AVInput.dialogdata.LtsRtsTio == LtsRtsTio_OLD:
                logfile.write(  str(now)+","+str(AVInput)+","+str(NaoCalgaze)+','+str(STT_txt)+","+str(NAO_txt)+","+
                                str(NaoHeadPos)+","+str(state)+","+str(DialogPhase)+","+
                                str(TakeTurn)+','+str(GazeBeforeS_SilenceBeforeG)+','+str(PreSilenceCutInDetected)+','+str(TTdelay)+'\n')
            else:
                logfile.write(  str(now)+","+str(AVInput)+","+str(NaoCalgaze)+','+str(STT_txt)+","+str(NAO_txt)+","+
                                str(NaoHeadPos)+","+str(state)+","+str(DialogPhase)+","+
                                str(TakeTurn)+','+str(GazeBeforeS_SilenceBeforeG)+','+str(PreSilenceCutInDetected)+','+str(TTdelay)+','+
                                str(AVInput.dialogdata.LtsRtsTio)+'\n')  
                                
            LtsRtsTio_OLD = AVInput.dialogdata.LtsRtsTio
            AVold = AVInput
    
    if CloseLog == True: 
        #logfile.write('\n'+str(AVInput.dialogdata))  # This is only the cumulative data from the 'moving window dialog stats'
        logfile.close()          

def printline(text, x=0):
    global EnablePytts
    """Print and depending on EnablePytts play PythonTTS. Waits for x seconds if EnablePytts is disabled."""
    
    print str(text)
    if EnablePytts == 1:
        if not text.startswith('*'):    # Text for debugging/info purposes only are not synthesized if prefix = *
            PyttsSay(text)
    else:
        time.sleep(x)

def TXTcode():
    global state
    global NameLeft
    global NameRight
    global AVInput
    global Lturns
    global Rturns
    
    return state, NaoHeadPos, NameLeft, NameRight, AVInput.KeyPressChar, Lturns, Rturns

def text():
    global utterance_text
    
    utterance_text = utterance(*TXTcode())
    
    return utterance_text

def NaoInitialize():
    global naoConn
    global motion
    global tts
    global trackface
    
    if naoConn:              
        # Initialize and create Proxy's to be used
        try:
            motion = ALProxy("ALMotion", naoIP, 9559)
            tts = ALProxy("ALTextToSpeech", naoIP, 9559)
            trackface = ALProxy("ALFaceTracker", naoIP, 9559)
        
            tts.setLanguage("English")
            tts.setVolume(0.8)
            tts.say("\RSPD=115\ "+"\VCT=85\ "+"Lets start") #RSPD=Speed, VCT=Pitch
            
            # enable stiffness only on head.
            motion.setStiffnesses("LArm", 0)
            motion.setStiffnesses("RArm", 0)
            motion.setStiffnesses("LLeg", 0)
            motion.setStiffnesses("RLeg", 0)
            motion.setStiffnesses("Head", 1) 
 
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
        
   
    if setHeadPos == 'L' or setHeadPos == 'R' or setHeadPos == '-':
        ManageFaceTracker(1, MotionSpeed)
    elif setHeadPos == 'B' and NaoHeadPos != '-':
        ManageFaceTracker(1, MotionSpeed*2)
    elif setHeadPos == 'B0' or (setHeadPos == 'B' and NaoHeadPos == '-'):
        ManageFaceTracker(1, MotionSpeed*4.5)
        
    if setHeadPos == 'L':
        textline = "*Nao turns head to the left"
        motion.post.angleInterpolation("Head", [angle(65), angle(-5)], MotionSpeed, True) if naoConn else printline(textline, MotionSpeed/2.0)
        NaoHeadPos = 'L'
    elif setHeadPos == 'R':
        textline = "*Nao turns head to the right"
        motion.post.angleInterpolation("Head", [angle(-65), angle(-5)], MotionSpeed, True) if naoConn else printline(textline, MotionSpeed/2.0)
        NaoHeadPos = 'R'
    elif setHeadPos == '-':
        textline = "*Nao turns head to neutral"
        motion.post.angleInterpolation("Head", [angle(0), angle(-5)], MotionSpeed, True) if naoConn else printline(textline, MotionSpeed/2.0)
        NaoHeadPos = '-'
    elif setHeadPos == 'B':
        textline = "*Nao shifts head back and forth between talking participants"
        if NaoHeadPos == 'R':
            motion.post.angleInterpolation("Head", [angle(65), angle(-5)], MotionSpeed, True) if naoConn else printline(textline, MotionSpeed/2.0)
            motion.post.angleInterpolation("Head", [angle(-65), angle(-5)], MotionSpeed, True) if naoConn else printline('*', MotionSpeed/2.0)
        elif NaoHeadPos == 'L':
            motion.post.angleInterpolation("Head", [angle(-65), angle(-5)], MotionSpeed, True) if naoConn else printline(textline, MotionSpeed/2.0)
            motion.post.angleInterpolation("Head", [angle(65), angle(-5)], MotionSpeed, True) if naoConn else printline('*', MotionSpeed/2.0)
        elif NaoHeadPos == '-':
             motion.post.angleInterpolation("Head", [angle(65), angle(-5)], MotionSpeed, True) if naoConn else printline(textline, MotionSpeed/2.0)
             motion.post.angleInterpolation("Head", [angle(-65), angle(-5)], MotionSpeed, True) if naoConn else printline('*', MotionSpeed/2.0)
             motion.post.angleInterpolation("Head", [angle(0), angle(-5)], MotionSpeed, True) if naoConn else printline('*', MotionSpeed/2.0)          
    elif setHeadPos == 'B0': 
        textline = "*Nao shifts head back and forth between listening participants AND ends in neutral position"
        if NaoHeadPos == 'R':
            motion.post.angleInterpolation("Head", [angle(65), angle(-5)], MotionSpeed*1.5, True) if naoConn else printline(textline, MotionSpeed/2.0)
            motion.post.angleInterpolation("Head", [angle(-65), angle(-5)], MotionSpeed*1.5, True) if naoConn else printline('*', MotionSpeed/2.0)
            motion.post.angleInterpolation("Head", [angle(0), angle(-5)], MotionSpeed*1.5, True) if naoConn else printline('*', MotionSpeed/2.0)
            NaoHeadPos = '-'
        elif NaoHeadPos == 'L':
            motion.post.angleInterpolation("Head", [angle(-65), angle(-5)], MotionSpeed*1.5, True) if naoConn else printline(textline, MotionSpeed/2.0)
            motion.post.angleInterpolation("Head", [angle(65), angle(-5)], MotionSpeed*1.5, True) if naoConn else printline('*', MotionSpeed/2.0)
            motion.post.angleInterpolation("Head", [angle(0), angle(-5)], MotionSpeed*1.5, True) if naoConn else printline('*', MotionSpeed/2.0)
            NaoHeadPos = '-'
        elif NaoHeadPos == '-':
             motion.post.angleInterpolation("Head", [angle(65), angle(-5)], MotionSpeed*1.5, True) if naoConn else printline(textline, MotionSpeed/2.0)
             motion.post.angleInterpolation("Head", [angle(-65), angle(-5)], MotionSpeed*1.5, True) if naoConn else printline('*', MotionSpeed/2.0)
             motion.post.angleInterpolation("Head", [angle(0), angle(-5)], MotionSpeed*1.5, True) if naoConn else printline('*', MotionSpeed/2.0)          


def MoveHeadDuringSpeech(string, MotionSpeed = 0.8, PauseBetween_ms = 3000, Xtimes=None):
    global NaoHeadPos  
    global naoConn
    
    WaitXms = PauseBetween_ms
    motionspeed = str(MotionSpeed)
    
    if Xtimes == None:
        words = re.split(r'[^0-9A-Za-z]+',string)
        if words[-1] == '':
            words = words[:-1]
        
        print len(words)
        
        sentences = int(math.floor(len(words)/20.0))
    else:
        sentences = Xtimes
        
    print sentences

    yawLR = ['angle(65)', 'angle(-65)']
    codeL = '(Lid = motion.post.angleInterpolation("Head", '+yawLR[0]+', angle(-5)], '+motionspeed+', True))'
    codeR = '(Rid = motion.post.angleInterpolation("Head", '+yawLR[1]+', angle(-5)], '+motionspeed+', True))'
    codeN = '(motion.post.angleInterpolation("Head", angle(0), angle(-5)], '+motionspeed+', True))'
    waitLR = ['(motion.wait(Lid, '+WaitXms+'))', '(motion.wait(Rid, '+WaitXms+'))']
    motionRL = [codeR, codeL]

    if sentences > 0:
        if NaoHeadPos != 'R':
            select()
            code = codeL
        else:
            code = codeR
    
    if sentences > 1:
        for i in range(1,sentences-1):
            LorR = select()
            code += '+'+str(waitLR[LorR])+'+'+str(motionRL[LorR])
    
    code += '+'+str(waitLR[select()])+'+'+ codeN
    NaoHeadPos = '-'
    
    print code
    
    if naoConn == 1:
        eval(code)

        
def Recalc_adaptTTDelay(sign=None):
    """ Staircase procedure to render appropriate stepsizes"""
    global staircase
    global TTwin
    global Cond1_fixedTTdelay
    global Cond2_adaptTTDelay
    global stepsize
    global maxStepsize
    global minStepsize
    global maxAdaptDelay
    global minAdaptDelay
    
    if stepsize == None:
        stepsize = 0.125 #(TTwin+Cond1_fixedTTdelay)*0.1  # Stepsize START VALUE in ms for the adaptive turn-take feedback-loop (default = 0.25)
        minStepsize = 0.02
        maxStepsize = 0.5 #(TTwin+Cond1_fixedTTdelay)*0.2 # One fith of the total window-span (default [TTwin 2.5] = 0.5)
        minAdaptDelay = 0
        maxAdaptDelay = TTwin+Cond1_fixedTTdelay
        
    if sign == '+' or sign == '-':
        # Shift register principle
        staircase = staircase[1:-1]+[staircase[-1]]+[sign]
    
        if staircase == ['+','+','+','+'] or staircase == ['-','-','-','-']:
            staircase = ['?','?','?',sign] # Reset staircase to avoid consecutive doubling of stepsize
            # Double current stepsize
            if stepsize*2.0 < maxStepsize:
                stepsize = stepsize*2.0
            elif stepsize*2.0 > maxStepsize or stepsize*2.0 == maxStepsize:
                stepsize = maxStepsize
                        
        elif staircase == ['+','-','+','-'] or staircase == ['-','+','-','+']:
            staircase = ['?','?','?',sign] # Reset staircase to avoid consecutive halving of stepsize
            # Halve current stepsize
            if stepsize*0.5 > minStepsize:
                stepsize = stepsize*0.5
            elif stepsize*0.5 < minStepsize or stepsize*0.5 == minStepsize:
                stepsize = minStepsize
        
        if sign == '+':
            if (Cond2_adaptTTDelay+float(stepsize)) < maxAdaptDelay:
                Cond2_adaptTTDelay += float(stepsize)
            elif (Cond2_adaptTTDelay+float(stepsize)) > maxAdaptDelay or (Cond2_adaptTTDelay+float(stepsize)) == maxAdaptDelay:
                Cond2_adaptTTDelay = maxAdaptDelay
        elif sign == '-':
            if (Cond2_adaptTTDelay-float(stepsize)) > minAdaptDelay:
                Cond2_adaptTTDelay -= float(stepsize)
            elif (Cond2_adaptTTDelay-float(stepsize)) < minAdaptDelay or (Cond2_adaptTTDelay-float(stepsize)) == minAdaptDelay:
                Cond2_adaptTTDelay = minAdaptDelay
            
    print "Sign =", sign, " ******* Stepsize = ", stepsize, " ******* Cond2_adaptTTDelay = ", Cond2_adaptTTDelay
    
    return Cond2_adaptTTDelay    

def NaoTakesTurn(turntypeID=1):
    global TakeTurn
    global TurnsSkipped
    global CutInDetected
    global PreSilence
    global GazeBeforeSilence
    global SilenceBeforeGaze
    global NaoHeadPos
    global state
    global naoConn
    
    TurnsSkipped = 0
    TakeTurn = turntypeID           # For logging purposes only
    
    if SpeechLRorB(AVInput) != '.': # This means Nao is going to interrupt someone by taking turn (i.e. cut-in)
        CutInDetected = True        # Always (independent from exp. cond.) register if a turn-take=cut-in          
            
    if ExpCond == 2 and turntypeID == 1: # Only adapt the Cond2_adaptTTDelay if Experiment condition = 2 and TT requirements are met
        if (PreSilence==False and CutInDetected==True) or (PreSilence==True and CutInDetected==False):
            # INCREASE delay by adding x ms, for which x is definded by a variable/fixed stepsize
            Recalc_adaptTTDelay('+')  
        elif (PreSilence==True and CutInDetected==True) or (PreSilence==False and CutInDetected==False):
            # DECREASE delay by subtracting x ms, for which x is definded by a variable/fixed stepsize
            Recalc_adaptTTDelay('-')
    """ #Alternative (better?) definition:        
        if (PreSilence==False and CutInDetected==True) or (PreSilence==False and CutInDetected==False):
            # INCREASE delay by adding x ms, for which x is definded by a variable/fixed stepsize
            Recalc_adaptTTDelay('+')  
        elif (PreSilence==True and CutInDetected==True) or (PreSilence==True and CutInDetected==False):
            # DECREASE delay by subtracting x ms, for which x is definded by a variable/fixed stepsize
            Recalc_adaptTTDelay('-') 
    """
        
    txt = text()
    if txt.startswith(PREFIX[0]*2,0,2): #Verdict sentence for which the next state must become 1
        state = 1
    elif txt.startswith(PREFIX[0],0,1): #Topic option sentence for which a Head-Turn is requested
        print "*Switch_turntake utterance detected, start non-blocking head movement to direct other participant"
        if NaoHeadPos == 'L':
            TurnHeadNaoto('R')
        elif NaoHeadPos == 'R':
            TurnHeadNaoto('L')
        state = 2
    else:                           #Topic option sentence for which nothing in addition is requested
        state = 2
        
    UpdateLog()                     # Log Turn-Take event
    tts.say(txt) if naoConn else printline(txt,4) #Use 'txt' not text() !    
    
    TakeTurn = 0                    # Reset values after logging and turntake
    CutInDetected = False
    GazeBeforeSilence = False
    SilenceBeforeGaze = False    
                
## ******************************************************************************************************************* ##
## ******************************************************************************************************************* ##
## ******************************************************************************************************************* ##                

if __name__ == "__main__": 
    naoIP = "192.168.0.114"
#    naoIP = "169.254.59.24"
    naoConn = 0                     # 1 = Nao is connected, 0 = Nao is NOT connected
    VoiceAudio = "mono"           # Select if you want to record mono or in stereo sound (default: stereo)
    EnablePytts = 0                 # If naoConn=False, sentences will be spoken by Python voice if EnablePytts=1
    ExpCond = 1        # !!!        # 1 = Conservative, 2 = Adaptive (gaze), 3 = Assertive
    TTwin = 2.0                     # Turn-Take (TT) WINDOW, a very important fixed variable to modify TT behavior
    Cond1_fixedTTdelay = 0.7        # Duration of required silence before a turn-take upon gaze cue is done when ExpCond = 1 (default = 0.7)
    Cond2_adaptTTDelay = 0.3        # START VALUE of the adaptive turn-take delay that is used if ExpCond = 2
    MAXsilence = 9.0                # If all Turn-Take cue combinations fail, take turn after X sec. of silence.
    SkipTurnTake = False            # Give fixed bolean 'True' or 'False' value
    MaxSkipTurns = 1                # The number of Turn-Passes between consecutive Turn-Takes
    gazetol = 8                     # Gaze tolerance in degrees
    DiffPerc = 0.2                  # Error marge used to determine if face new sample frame is valid (Default = 0.2)
    MotionSpeed = 0.8               # The speed of the actuators with which the Nao performs movements
    MeanSystemDelay = 0#0.140        # To take into account the estimated lag in seconds from sample settings and processing time
    
    SessionID = "Post_experiment_run"  
    NameLeft = "Maus"
    NameRight = "Stranger"
    
    raw_input("REMINDER: Nao blinking activated? All variables correctly set? (press ENTER to continue): ")
#    SessionID = raw_input("Give current SessionID: ")
#    NameLeft = raw_input("Give (only!) first name of participant on the LEFT of Nao: ")
#    NameRight = raw_input("Give (only!) first name of participant on the Right of Nao: ")


    try:
        UpdateLog(CreateHeader=True)
        while CONTINUE:
            
            time.sleep(0) if naoConn else time.sleep(0.01)  #To limit maximum loop frequence if naoConn == 0
            
            if pauzed == 'p' and AVInput.KeyPressChar != 'p':
                pauzed = '_'            
            elif pauzed == '_' and AVInput.KeyPressChar == 'p':
                print "State-system is pauzed. Press 'p' again for the program to continue..."
                while pauzed != 'p':
                    AVInput = SUB.GetAVInput(naoIP, naoConn, MonoStereo=VoiceAudio)
                    if pauzed == '_' and AVInput.KeyPressChar != 'p':
                        pauzed = AVInput.KeyPressChar
                    elif pauzed != '_':
                        pauzed = AVInput.KeyPressChar
                    time.sleep(0.01)
                functionsRESET(-1,0)
                
            if AVInput.KeyPressChar == 'r': # In case head-yaw gets misaligned, this enables instant recalibration
                if NaoHeadPos == 'R':
                    deviation['R'] = AVInput.headposeYaw
                elif NaoHeadPos == 'L':
                    deviation['L'] = AVInput.headposeYaw
                    
            UpdateLog()
            functionsRESET(state, TurnsSkipped)
            AVInput = SUB.GetAVInput(naoIP, naoConn, MonoStereo=VoiceAudio)
            Lturns = AVInput.dialogdata.LturnCount
            Rturns = AVInput.dialogdata.RturnCount
            setUtteranceVARs(*TXTcode()) # Keep the utterence script in 'synchronization' by passing some main variables
            silentfor(AVInput)  # Always keep silent counter updated (i.e. independant from current state, only 'resets' if not silent)
            ManageFaceTracker() # Always keep the facetracker manager updated to automatically enable it again after x time.
            
            if state > 0:
                NaoCalgaze = TrueGaze(NaoHeadPos, AVInput)
                NaoLEDs(NaoHeadPos, AVInput)
                if (AVInput.facedetected and  # Several requirements to ensure proper input for the face/gaze recognition
                    AVold.facesize*(1-DiffPerc) < AVInput.facesize < AVold.facesize*(1+DiffPerc) and
                    AVInput.facesize > 80): # the dimensions must be at least 100 pixels
                    ValidFace = True
                else:
                    ValidFace = False
            
            print "\nCurrent state =", state
            print "Nao gazes to the =", NaoHeadPos
            if ExpCond == 1:
                print "Cond1_fixedTTDelay =", Cond1_fixedTTdelay
            elif ExpCond == 2:
                print "Cond2_adaptTTDelay =", Cond2_adaptTTDelay
            elif ExpCond == 3:
                print "Cond3_systemDelay =  0.140" #, MeanSystemDelay
            print "Calibrated gaze = ", NaoCalgaze
            print str(AVInput)
#            print str(AVInput.STTwords)
#            print str(AVInput.dialogdata.liveWindow)    
#            print str(AVInput.dialogdata)   

            if state == 0:
                NaoInitialize()
                """ 
            # Nao motion testing code
                
                trackface.stopTracker() if naoConn else printline("*trackface.startTracker()", 1)
                textline = "*Nao turns head to the right"
                motion.setAngles("Head", [angle(-65), angle(-5)], MotionSpeed) if naoConn else printline(textline, MotionSpeed/2.0)
                textline = "Nao init done, start motion test in 3 sec..."  
                print textline
                tts.say(textline) if naoConn else printline(textline, 1)
                time.sleep(3)
                textline = "*Nao shifts head back and forth between talking participants"
                TurnHeadNaoto('B')
#                motion.post.angleInterpolation("Head", [angle(65), angle(-5)], MotionSpeed, True) if naoConn else printline(textline, MotionSpeed/2.0)
#                motion.post.angleInterpolation("Head", [angle(-65), angle(-5)], MotionSpeed, True) if naoConn else printline('*', MotionSpeed/2.0)
#                motion.post.angleInterpolation("Head", [angle(65), angle(-5)], MotionSpeed, True) if naoConn else printline('*', MotionSpeed/2.0)          
                textline = "Hi there, my name is Marvin, who are you? Welcome to the use lab and our little discussion group"
                tts.say(textline) if naoConn else printline(textline, 1)
                state = 99
            if state == 99:
                raw_input("Press CTRL+C before pressing ENTER")
            elif state == 300:
#                """        
                textline = ("Welcome to the use lab and our little discussion group, I will explain more to you in a short moment, "+
                "but before we introduce ourselves I would like you to be absolutely quiet for 2 seconds.")
#                TurnHeadNaoto('B')
                tts.say(textline) if naoConn else printline(textline, 1)
                time.sleep(1)

                while SUB.printinfo != 2:   #Run microphone background noise calibration
                    AVInput = SUB.GetAVInput()
                    time.sleep(0.01)
                    
                TurnHeadNaoto('R')   
                textline = "Hi there, my name is Marvin. Who are you, only look at me while briefly introducing yourself!"
                tts.say(textline) if naoConn else printline(textline, 1)
                initcal = None
                warning = 0
                trackface.startTracker() if naoConn else printline("*trackface.startTracker()", 1)
                while initcal == None:   # If calibration fails, output stays type 'None', otherwise output = 0
                    initcal = TrueGaze(NaoHeadPos, AVInput, True)
                    if initcal == None:
                        if warning >= 5:
                            warning = 0
                            textline = "For calibration reasons, please only look at me from a fixed position and try not to move your head"
                            tts.say(textline) if naoConn else printline(textline, 1)
                            rerun = raw_input("Calibration FAILED, press ENTER to re-run calibration: ")
                        else:
                            warning += 1
                    if initcal != None:
                         rerun = raw_input("Press r + ENTER to re-run calibration, otherwise just hit ENTER: ")
                         if rerun == 'r':
                             initcal = None
#                while not(silentfor(AVInput, 1.5)):
#                    AVInput = SUB.GetAVInput()
#                    time.sleep(0.05)
                sys.stdout.write("\n")
                textline = "Welcome "+NameRight+", nice to meet you."
                tts.say(textline) if naoConn else printline(textline, 1)
                
                
                TurnHeadNaoto('L')
                textline = "You also welcome of course! Please introduce yourself, and remember only to look at me while talking!"
                tts.say(textline) if naoConn else printline(textline, 1)
                initcal = None
                warning = 0
                trackface.startTracker() if naoConn else printline("*trackface.startTracker()", 1)
                while initcal == None:   # If calibration fails, output stays type 'None', otherwise output = 0
                    initcal = TrueGaze(NaoHeadPos, AVInput, True)
                    if initcal == None:
                        if warning >= 5:
                            warning = 0
                            textline = "For calibration reasons, please only look at me from a fixed position and try not to move your head"
                            tts.say(textline) if naoConn else printline(textline, 1)
                            rerun = raw_input("Calibration FAILED, press ENTER to re-run calibration: ")
                        else:
                            warning += 1
                    if initcal != None:
                         rerun = raw_input("Press r + ENTER to re-run calibration, otherwise just hit ENTER: ")
                         if rerun == 'r':
                             initcal = None
                initA = 0  # To reset the silencefor timer (is exceptional since this happens automatically when not silent & state > 0)
#                while not(silentfor(AVInput, 1.5)):
#                    AVInput = SUB.GetAVInput()
#                    time.sleep(0.05)
                sys.stdout.write("\n")
                textline = "Nice to meet you too "+NameLeft+"!" 
                tts.say(textline) if naoConn else printline(textline, 1)
                
                
                TurnHeadNaoto('-')
                tts.say(text()) if naoConn else printline(text(), 2)    # Introduction and explination of experiment
                
#                """
                TurnHeadNaoto('R')
                textline = "Everything clear and ready to start "+NameRight+"?"
                tts.say(textline) if naoConn else printline(textline)
                trackface.startTracker() if naoConn else printline("*trackface.startTracker()", 1)
                raw_input("Press ENTER to confirm readyness of participant 1 of 2 (%s):" %(NameRight))
                
                TurnHeadNaoto('L')
                textline = "Everything clear and ready for you also "+NameLeft+"?"
                tts.say(textline) if naoConn else printline(textline)
                trackface.startTracker() if naoConn else printline("*trackface.startTracker()", 1)
                raw_input("Press ENTER to confirm readyness of participant 2 of 2 (%s):" %(NameLeft))
#                """
                tts.say(text()) if naoConn else printline(text(), 2)
                SUB.GetAVInput(RstData=1)   # Resets audio dialog data to remove recordings from state 0.
                state = 1
                
            elif state == 1:
                txt = text()
                if txt.startswith(PREFIX[0],0,1):
                    CONTINUE = False
                TurnHeadNaoto('B0') # Nao shakes head
                tts.say(txt) if naoConn else printline(txt, 4) # Aks new question with new options OR end dialog
                state = 2                                      # Use 'txt' not text() !

            elif state == 2:
                if silentfor(AVInput, 4.0):
                    state = 3    
                elif someonespeaksfor(0.5, AVInput):
                    state = 4
                
            elif state == 3:
                TurnHeadNaoto('B') # Nao shakes head
                tts.say(text()) if naoConn else printline(text(),2) #To break initial silence (e.g. shy subjects)
                state = 2
             
            elif state == 4:
                if SpeechLRorB(AVInput) == 'L' and NaoHeadPos != 'L':
                    TurnHeadNaoto('L')
                elif SpeechLRorB(AVInput) == 'R' and NaoHeadPos != 'R':
                    TurnHeadNaoto('R')
#                elif SpeechLRorB(AVInput) == 'B':
#                    TurnHeadNaoto('B')
                state = 6
                
            elif state == 5:
                #To appear more alive, Nao will just say a very short utterance (not part of analysis)
                tts.say(text()) if naoConn else printline(text(),1)
                state = 6
                
            elif state == 6:
                if otherspeaksfor(0.5, AVInput, NaoHeadPos):
                    state = 4
                elif SameSpeakerfor(4.0, AVInput):
                    state = 5
                elif silentfor(AVInput, MAXsilence):     # This condition is necessary to ensure dialog flow
                    GazeBeforeSilence = False
                    SilenceBeforeGaze = False
                    GazeBeforeXDelay = False
                    if TurnsSkipped == 0:
                        TurnHeadNaoto('B') # Nao shakes head
                        tts.say("Anything else?") if naoConn else printline("Anything else?",2) #To break the silence
                        TurnsSkipped += 1
                    elif TurnsSkipped > 0:
                        TurnsSkipped = 0
                        NaoTakesTurn(2) # A fallback turn-take action to ensure dialog flow, next state (!=6) is automatically set
                else:
                    
                    LooksAtNao = (ValidFace and LookingAtNao(NaoHeadPos, AVInput))  # Returns boolean: True if Nao is looked at

                    if ExpCond == 1: # 1 = Conservative
                        print "SilenceBeforeGaze =", SilenceBeforeGaze
                        print "GazeBeforeSilence =", GazeBeforeSilence
                        if GazeBeforeSilence == False and SilenceBeforeGaze == False:
                            if LooksAtNao:
                                GazeBeforeSilence = TrueForXSeconds(TTwin)
                            elif silentfor(AVInput, Cond1_fixedTTdelay):
                                SilenceBeforeGaze = TrueForXSeconds(TTwin)
                            
                        if GazeBeforeSilence:
#                            # 4 lines below are an post-experiment addition!
#                            if LooksAtNao == False:
#                                GazeBeforeSilence = False
#                                TrueForXSeconds(reset)
#                            else:
                                GazeBeforeSilence = TrueForXSeconds(TTwin+Cond1_fixedTTdelay)    # Update to newest value
                                if GazeBeforeSilence and silentfor(AVInput, Cond1_fixedTTdelay): # check if updated value is still valid
#                                    GazeBeforeSilence = False (is done in the NaoTakesTurn() function)
                                    TrueForXSeconds(reset)
                                    if SkipTurnTake and TurnsSkipped < MaxSkipTurns:
                                        print "Turn Skipped"
                                        TurnsSkipped += 1
                                    else:
                                        NaoTakesTurn() # next state (!=6) is automatically set
                                        print "Conservative Gaze-Before-Silence Turn-Take moment detected"
                                    
                        elif SilenceBeforeGaze:
                            if SpeechLRorB(AVInput) != '.':
                                SilenceBeforeGaze = False
                                TrueForXSeconds(reset)
                            else:
                                SilenceBeforeGaze = TrueForXSeconds(TTwin)  # Update to newest value
                                if SilenceBeforeGaze and LooksAtNao:        # check if updated value is still valid
#                                    SilenceBeforeGaze = False (is done in the NaoTakesTurn() function)
                                    TrueForXSeconds(reset)
                                    if SkipTurnTake and TurnsSkipped < MaxSkipTurns:
                                        print "Turn Skipped"
                                        TurnsSkipped += 1
                                    else:
                                        NaoTakesTurn() # next state (!=6) is automatically set
                                        print "Conservative Silence-Before-Gaze Turn-Take moment detected"
                                
                    elif ExpCond == 2: # 2 = Adaptive
                        temp = silentfor(AVInput, 0.1)
                        print "PreSilence = ", PreSilence   
                        if LooksAtNao and GazeBeforeXDelay == False: 
                            PreSilence = temp
                            GazeBeforeXDelay = True
                            
                        if (LooksAtNao or GazeBeforeXDelay) and AdaptiveDelayPassed(): # AdaptiveDelayPassed is updated and checked
                            GazeBeforeXDelay = False                      
                            if SkipTurnTake and TurnsSkipped < MaxSkipTurns:
                                print "Turn Skipped"
                                TurnsSkipped += 1
                            else:
                                NaoTakesTurn() # next state (!=6) is automatically set
                                print "Adaptive Turn-Taking moment, based on gaze + unconditional adaptive delay"
                                    
                    elif ExpCond == 3:  #3 = Assertive 
                        # Maybe it is better to simplify this condition to simoultanious gaze+silence=TT (i.e. not use TTwin)
                        print "GazeBeforeSilence =", GazeBeforeSilence
                        if LooksAtNao or GazeBeforeSilence:
                            GazeBeforeSilence = TrueForXSeconds(TTwin)               # Update to newest value
                            if GazeBeforeSilence and SpeechLRorB(AVInput) == '.':    # check if updated value is still valid
                                GazeBeforeSilence = False
                                TrueForXSeconds(reset)
                                if SkipTurnTake and TurnsSkipped < MaxSkipTurns:
                                    print "Turn Skipped"
                                    TurnsSkipped += 1
                                else:
                                    NaoTakesTurn() # next state (!=6) is automatically set
                                    print "Assertive Turn-Take moment, based on gaze + instance of silence"

    except KeyboardInterrupt:
        print "User terminating state-sequence script"
        pass
    try:
        pytts.stop()
        pytts.endLoop()
    except:
        pass
    UpdateLog(CloseLog=True)
    SUB.GetAVInput(stop=1)
    motion.setStiffnesses("Body", 0) if naoConn else printline("*Stiffness disabled")