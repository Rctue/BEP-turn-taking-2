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
import vision_definitions as vd
import camera_script as CAM
import sys
import time

printinfo = 0
iteration = 0
Exit = 0
RST = 0

class Vdata:
    def __init__(self,iteration = '-', facedetected = '-', facecenter = ['-','-'], facesize = '-',
                 faceradians = ['-','-'], headpose = ['-','-'], KeyPressChar = '?'):
        self.iter = iteration     
        self.facedetected = facedetected
        self.facecenter = facecenter
        self.facecenterX = facecenter[0]
        self.facecenterY = facecenter[1]
        self.facesize = facesize
        self.faceradians = faceradians
        self.faceradiansHorz = faceradians[0]
        self.faceradiansVert = faceradians[1]
        self.headpose = headpose
        self.headposeYaw = headpose[0]
        self.headposePitch = headpose[1]
        self.KeyPressChar = KeyPressChar
    
    def __str__(self):
        stringtext = str('{%s}' %(self.iter)+
                         ', %s' %(self.facedetected)+
                         ', %s' %(self.facecenter)+
                         ', %s' %(self.facesize)+
                         ', %s' %(self.faceradians)+
                         ', %s' %(self.headpose)+
                         ', %s' %(self.KeyPressChar))
        return stringtext

       
def funcV(qV, qStop, naoIP, naoConn):
    global Exit

    while Exit != 1:
        if qStop.empty():
            FACE = CAM.GetFaceData(facedetectTYPE=1, 
                                   faceYawPitchON=1, 
                                   NAO_IP=naoIP, 
                                   indexEXTERNALcam=0,      # Limited use for external webcams (raw captures) only
                                   CreateVideoFile=0,
                                   useNAOcam=1, 
                                   dimension=vd.kVGA, 
                                   maxFPS=30)
            qV.put(FACE)
        else:
            print "CAM.ExitCamera()"
            sys.stdout.flush()
            CAM.ExitCamera()
            Exit = 1
            
def VideoData(naoIP="192.168.0.114", naoConn=0, stop=0, RstData=0):
    global iteration
    global AVoutput
    global AVout
    global qStop
    global qRstData
    global pV
    global qV
    global get
         
    
    if stop == 0 and iteration == 0:
        qV = Queue(1)
        qStop = Queue(1)
        qRstData = Queue(1)
        AVoutput=['-']
        AVout = Vdata()
        get = 0
        print "Multi_SUBprocess started"
        pV = Process(target = funcV, args=(qV,qStop,naoIP,naoConn,))
        pV.start()
        
        iteration += 1 
       
        
    if stop == 0 and iteration != 0:
        
        if RstData != 0:
            qRstData.put(1)
            
        if not qV.empty():
            AVoutput[0] = qV.get()
            get = 1       


        if get == 1:
            
            try:
                AVout = Vdata(iteration, 
                               AVoutput[0][0],
                               AVoutput[0][1],
                               AVoutput[0][2],
                               AVoutput[0][3], 
                               AVoutput[0][4],
                               AVoutput[0][5])
                    
                get = 0
     
            except:
                sys.stdout.write('.')
                    
        iteration += 1
        
    if stop == 1:
        print "STOP requested by user"
        qStop.put(stop)
        time.sleep(1)
        pV.terminate()
        qV.close()
        print "All processes stopped correctly :)"
    
    return AVout