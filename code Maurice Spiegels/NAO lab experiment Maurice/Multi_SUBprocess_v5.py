# -*- coding: utf-8 -*-
"""
Created on Wed Sep 24 14:13:38 2014

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
from vision_definitions import kQQVGA, kQVGA, kVGA, k4VGA, k960p
import Multithread_microphone_input_test_v6 as MIC
import Multithread_lib_headpose_NN_modified_nao_v4 as CAM
import Read_DNSnuance_sttLogfile_v2 as STT
import sys
import time

printinfo = 0
iteration = 0
Exit = 0
RST = 0

class AVdata:
    def __init__(self,iteration = '-',mic = '-', facedetected = '-', facecenter = ['-','-'], facesize = '-',
                 faceradians = ['-','-'], headpose = ['-','-'], dialogdata = MIC.DialogStats(), 
                 KeyPressChar = '?', STTwords = ['-']):
        self.iter = iteration     
        self.mic = mic
        self.facedetected = facedetected
        self.facecenter = facecenter
        self.facesize = facesize
        self.facecenterX = facecenter[0]
        self.facecenterY = facecenter[1]
        self.faceradians = faceradians
        self.faceradiansHorz = faceradians[0]
        self.faceradiansVert = faceradians[1]
        self.headpose = headpose
        self.headposeYaw = headpose[0]
        self.headposePitch = headpose[1]
        self.dialogdata = dialogdata
        self.KeyPressChar = KeyPressChar
        self.STTwords = STTwords
    
    def __str__(self):
        stringtext = str('{%s}' %(self.iter)+
                         ', %s' %(self.mic)+
                         ', %s' %(self.facedetected))#+
#                         ', %s' %(self.facecenter)+      #WARNING: If un-commented Logfiles could become scrambled!
#                         ', %s' %(self.facesize)+
#                         ', %s' %(self.headposeYaw))
        return stringtext

def funcW(qW, qStop):
    global Exit
    
    while Exit != 1:
        if qStop.empty():
            WORDS = STT.GetWords(PollingRate=0.1)
            qW.put(WORDS)
        else:
            print "STT.ExitGetWords()"
            sys.stdout.flush()
            STT.GetWords(stop=True)
            Exit = 1

def funcA(qA, qStop, qRstData, MonoStereo):
    global Exit
    global RST

    while Exit != 1:
        
        if RST != 0:
            RST = 0
        if not(qRstData.empty()):
            RST = qRstData.get()
            #print "dialogstats RST = True"
            sys.stdout.flush()
        if qStop.empty():       
            OLRB = MIC.DetectSound(DEVICE_INDEX=0, 
                                   SAMPLERATE=44100,        # Default = 44100
                                   INPUT_BLOCK_TIME=0.02,   # Default = 0.02
                                   CHANNELS=MonoStereo, 
                                   CreateAudioFile=0,
                                   voice_threshold=0.01,    # Default = 0.01
                                   intervalbuffer=7,        # Default = 7   or floor((0.05/INPUT_BLOCK_TIME)*3)
                                   peakbuffer=2,            # Default = 2   or floor((0.05/INPUT_BLOCK_TIME)*1)
                                   WindowSizeSec=1,         # Default = 1   to reduce processing time, otherwise use >=30
                                   resetData=RST)
            qA.put(OLRB)
        else:
            print "MIC.ExitMicrophone()"
            sys.stdout.flush()
            MIC.ExitMicrophone()
            Exit = 1
       
def funcV(qV, qStop, naoIP, naoConn):
    global Exit

    while Exit != 1:
        if qStop.empty():
            FACE = CAM.GetFaceData(facedetectTYPE=1, 
                                   faceYawPitchON=1, 
                                   NAO_IP=naoIP, 
                                   indexEXTERNALcam=0,      
                                   CreateVideoFile=0,       # Limited use for external webcams (raw captures) only
                                   useNAOcam=naoConn, 
                                   dimension=kVGA,          #| kQQVGA,    kQVGA,     kVGA,      k4VGA,      k960p      |#
                                   maxFPS=30)               #| (160x120), (320x240), (640x480), (1280x720), (1280x960) |#
            qV.put(FACE)
        else:
            print "CAM.ExitCamera()"
            sys.stdout.flush()
            CAM.ExitCamera()
            Exit = 1
            
def GetAVInput(naoIP="192.168.0.114", naoConn=0, MonoStereo="stereo", stop=0, RstData=0):
    global iteration
    global AVoutput
    global AVout
    global words
    global qStop
    global qRstData
    global pA
    global pV
    global pW
    global qA
    global qV
    global qW
    global get
    global printinfo
         
    
    if stop == 0 and iteration == 0:
        qA = Queue(1)
        qV = Queue(1)
        qW = Queue(1)
        qStop = Queue(1)
        qRstData = Queue(1)
        AVoutput=['-','-']
        AVout = AVdata()
        words=[]
        wordsTEMP = None
        get = 0
        printinfo = 0
        print "Multi_SUBprocess started"
        pA = Process(target = funcA, args=(qA,qStop,qRstData,MonoStereo,))
        pV = Process(target = funcV, args=(qV,qStop,naoIP,naoConn,))
        pW = Process(target = funcW, args=(qW,qStop,))
        pA.start()
        pV.start()
        pW.start()
        
        iteration += 1 
       
        
    if stop == 0 and iteration != 0:
        
        if RstData != 0:
            qRstData.put(1)
            
        if not qA.empty():
            AVoutput[0] = qA.get()
            get = 1
        if not qV.empty():
            AVoutput[1] = qV.get()
            get = 1      
        if not qW.empty():
            wordsTEMP = qW.get()
            if wordsTEMP != ['<???>']:
                words = wordsTEMP
                get = 1     


        if get == 1:
            
            try:
                AVout = AVdata(iteration, 
                               AVoutput[0][0], 
                               AVoutput[1][0],
                               AVoutput[1][1],
                               AVoutput[1][2],
                               AVoutput[1][3], 
                               AVoutput[1][4],
                               AVoutput[0][1], 
                               AVoutput[1][5], 
                               words)
                    
                get = 0
                
                if printinfo == 0 and AVoutput[0][0] == '-':
                    sys.stdout.write('Measuring audio background noise & initializing video stream')
                    printinfo = 1
                elif printinfo == 1 and AVoutput[0][0] == '-':
                    sys.stdout.write('.')
                elif printinfo == 1 and AVoutput[0][0] != '-':
                    sys.stdout.write('Done!\n')
                    printinfo = 2
                elif printinfo == 0 and AVoutput[0][0] != '-':
                    sys.stdout.write('Measuring audio background noise & initializing video stream...\nDone!\n')
                    printinfo = 2
     
            except:
                if printinfo == 0:
                    sys.stdout.write('Measuring audio background noise & initializing video stream...\n')
                    printinfo = 1
                elif printinfo == 1:
                    sys.stdout.write('.')
                    
        iteration += 1
        
    if stop == 1:
        print "STOP requested by user"
        qStop.put(stop)
        time.sleep(1)
        pA.terminate()
        pV.terminate()
        pW.terminate()
        qA.close()
        qV.close()
        qW.close()
        print "All processes stopped correctly :)"
    
    return AVout