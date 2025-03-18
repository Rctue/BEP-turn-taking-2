# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 10:55:09 2014

@author: Maurice Spiegels
"""

import pyaudio
pa = pyaudio.PyAudio()
import wave
import numpy
import math
import time
import datetime
import sys
global stream

LturnCnt = 0
RturnCnt = 0
WinSize = 60
printwindow = ''
lineprintCnt = 0
lineprintHeader = {0:"DialogStats Left Utterance timings (s):  ", 
                   1:"DialogStats Left Silences timings (s):  ",
                   2:"DialogStats Right Utterances timings (s):  ",
                   3:"DialogStats Right Silences timings (s):  ",
                   4:"DialogStats Turn-change Intervals (s):  ",
                   5:"DialogStats Turn-change Overlaps (s):  "}
        
stream = 0
initialize = 0
amp = [0.0,0.0]
OLRB = "-"
#fileframes = []
ExitAudioFile = None
calibrationDONE = False
InitAudiofile = True
initStats = 0
FORMAT = pyaudio.paInt16 
SHORT_NORMALIZE = (1.0/32768.0) # 16-bit == 65536 == +-32768 (one bit is used as sign)

class mic_channel:
    def __init__(self):
        self.L = []
        self.R = []

class DialogStats:
    def __init__(self, meanTurnLength = 0., turnCount = 0, meanIntervalLength = 0, meanIntervalFreq = 0, 
                 turnSilenceTime = 0, turnSilenceFreq = 0, turnOverlapTime = 0, turnOverlapFreq = 0, 
                 liveWindow = '', listEnds = [0,0,0,0,0,0]
                 ):
        self.LmeanTurnLength = meanTurnLength
        self.LturnCount = turnCount
        self.LmeanIntervalLength = meanIntervalLength
        self.LmeanIntervalFreq = meanIntervalFreq
        self.RmeanTurnLength = meanTurnLength
        self.RturnCount = turnCount
        self.RmeanIntervalLength = meanIntervalLength
        self.RmeanIntervalFreq = meanIntervalFreq
        self.turnSilenceTime = turnSilenceTime
        self.turnSilenceFreq = turnSilenceFreq
        self.turnOverlapTime = turnOverlapTime
        self.turnOverlapFreq = turnOverlapFreq
        self.liveWindow = liveWindow
        self.LtsRtsTio = listEnds #Left: turn, silence #Right: turn, silence #TurnChange: interval, overlap
        
    def __str__(self):
        stringtext = str(   'LmeanTurnLength = %s      \t' %(self.LmeanTurnLength)+
                            ',RmeanTurnLength = %s     \t' %(self.RmeanTurnLength)+
                            ',turnSilenceTime = %s     \n' %(self.turnSilenceTime)+
                            'LturnCount = %s           \t' %(self.LturnCount)+
                            ',RturnCount = %s          \t' %(self.RturnCount)+
                            ',turnSilenceFreq = %s     \n' %(self.turnSilenceFreq)+
                            'LmeanIntervalLength = %s  \t' %(self.LmeanIntervalLength)+
                            ',RmeanIntervalLength = %s \t' %(self.RmeanIntervalLength)+
                            ',turnOverlapTime = %s     \n' %(self.turnOverlapTime)+
                            'LmeanIntervalFreq = %s    \t' %(self.LmeanIntervalFreq)+
                            ',RmeanIntervalFreq = %s   \t' %(self.RmeanIntervalFreq)+
                            ',turnOverlapFreq = %s     \n' %(self.turnOverlapFreq)
                        )
        return stringtext

DataOut = DialogStats()
DialogData = DialogStats()
    
def ShiftAppend(timestamp, newvalue, listX=[]): # Save dialog parameter in corresponding list
    global WinSize
    
    newvalue = round(newvalue,2)
    listX.append([timestamp,newvalue])
    Wstart = float(timestamp-WinSize)
    
    while listX[0][0] <= Wstart:       # Limit list length to given window length (in seconds)
        listX.pop(0)
        if len(listX) == 0:
            break
    
    return listX
    
def ListMean(listX=[]):
    global printwindow
    global lineprintCnt
    # Means are caluculated for all 6 lists, therefore the 'printwindow' string is build within this function
    
    if lineprintCnt == 6:
        lineprintCnt = 0
        printwindow = ''
    
    printwindow += lineprintHeader[lineprintCnt]
        
    if len(listX)>0:
        ListSum = 0
        for i in range (0,len(listX)):
            ListSum += listX[i][1]
            printwindow += str(listX[i][1])+', '
        mean = ListSum/len(listX)
    else:
        mean = 0
        
    printwindow = printwindow[:-2]+'\n'
    lineprintCnt += 1
        
    return mean

def getLtsRtsTio(ListwithLists=[]):
    out = []
    for l in range(0,len(ListwithLists)):
        try:
            out.append(ListwithLists[l][-1][1])
        except:
            out.append(0)
    
    return out
   
def UpdateDialogData(MicIn, Wsize, rstDialogData):
    global initStats
    global nulltime
    global PrevMic
    global PreSilence
    global PreOverlap
    global Lstart
    global Lend
    global Lt_list
    global Rstart
    global Rend
    global Rt_list
    global Bstart
    global Bend    
    global To_list
    global Sstart
    global Send
    global Ls_list
    global Rs_list
    global Ti_list
    global SilenceTemp
    global OverlapTemp
    global validL
    global validR
    global LturnCnt
    global RturnCnt
    global now
    global WinSize
    global printwindow
    
    #--------------------------------------------------
    def TemptoList(valid, timetoadd=0):
        """negative timing errors SHOULD BE SOLVED for this function!"""
        global SilenceTemp
        global OverlapTemp
        global now
        global Ti_list
        global Ls_list
        global Rs_list
        global To_list
        
        if valid == 1:
            if SilenceTemp[1] != '-':       # Since valid is 1: Check if temp data is present, if so, process it.

                time = SilenceTemp[0]
                if time < 0:                # to avoid negative timing errors (THIS ERROR SHOULD BE RESOLVED!)
                    SilenceTemp = [0,'-']   # 'clear' temp storage
                elif time > 5:              # Measuring a silence greater then 5 seconds is useless (i.e. dead dialog)
                    time = 5
                    
                if SilenceTemp[1] == 'T':
                    Ti_list = ShiftAppend(now, time, Ti_list)
                elif SilenceTemp[1] == 'L':
                    Ls_list = ShiftAppend(now, time, Ls_list)
                elif SilenceTemp[1] == 'R':
                    Rs_list = ShiftAppend(now, time, Rs_list)
                SilenceTemp = [0,'-']       # 'clear' temp storage
                
            if OverlapTemp[1] != '-':       # Since valid is 1: Check if temp data is present, if so, process it.
                
                time = OverlapTemp[0]
                if time < 0:                # to avoid negative timing errors (THIS ERROR SHOULD BE RESOLVED!)
                    OverlapTemp = [0,'-']   # 'clear' temp storage
                elif time > 5:              # More than 5 second overlap is very unnatural (i.e. only done on purpose)
                    time = 5
                    
                if OverlapTemp[1] == 'T':
                    To_list = ShiftAppend(now, time, To_list)
                    
        elif valid == 0: # negative timing errors are not avoided in this case (THIS ERROR SHOULD BE RESOLVED!)
            if SilenceTemp[1] != '-':         # Since valid is 0:
                SilenceTemp[0] += timetoadd   # add invalid speech time to silence period
                
            if OverlapTemp[1] != '-':
                OverlapTemp[0] += timetoadd   # add invalid speech time to overlap period
    #--------------------------------------------------    
    
    now = time.clock()
    WinSize = Wsize
    UtteranceMinLength = 0.10 # define in seconds (experiment value was 0.10, adviced = 1.0 thereby excluding verbal back-channel utterances)
    
    if rstDialogData != 0:
        print "dialogstats RST intern = True"
        sys.stdout.flush()
        initStats = 0         # resets dialog data recordings
                    
    if initStats == 0:
        Lt_list = []
        Rt_list = []
        To_list = [] #Turn-change overlap period
        Ls_list = [] #Left person interval silence
        Rs_list = [] #Right person interval silence
        Ti_list = [] #Turn boundry silence
        SilenceTemp = [0,'-'] #Temp storage for silence period which has to be verified before storage in silence list (Ti_list)
        OverlapTemp = [0,'-'] #Temp storage for overlap period which has to be verified before storage in overlap list (Ti_list)
        nulltime = time.clock()
        PrevMic = MicIn
        validL = 0
        validR = 0
        PreSilence = '-'
        PreOverlap = '-'
        Lstart = now
        Lend = now
        Rstart = now
        Rend = now   
        Bstart = now
        Bend = now
        Sstart = now
        Send = now
        initStats = 1
    
    elif initStats != 0:     # 'elif' and NOT 'if'. Since you want to preserve the previous MicIn value for comparison NEXT time
            
        if PrevMic == MicIn:
            if MicIn == 'L':
               Lend = now
            elif MicIn == 'R':
                Rend = now
            elif MicIn == 'B':
                Lend = now
                Rend = now
                Bend = now
            elif MicIn == '.':
                Send = now
        else:
            if PrevMic == 'L':
                if Lend-Lstart > UtteranceMinLength: #You cannot have had a proper turn if it lasted for less than x seconds
                    LturnCnt += 1
                    Lt_list = ShiftAppend(now, Lend-Lstart, Lt_list)
                    validL = 1
                    TemptoList(validL)
                else:
                    validL = 0
                    TemptoList(validL, Lend-Lstart)
            elif PrevMic == 'R':
                if Rend-Rstart > UtteranceMinLength:
                    RturnCnt += 1
                    Rt_list = ShiftAppend(now, Rend-Rstart, Rt_list) 
                    validR = 1
                    TemptoList(validR)
                else:
                    validR = 0
                    TemptoList(validR, Rend-Rstart)
            elif PrevMic == 'B':
                if Lend-Lstart > UtteranceMinLength:
                    LturnCnt += 1
                    Lt_list = ShiftAppend(now, Lend-Lstart, Lt_list)
                    validL = 1
                    TemptoList(validL)
                else:
                    validL = 0
                    TemptoList(validL, Lend-Lstart)
                if Rend-Rstart > UtteranceMinLength:
                    RturnCnt += 1
                    Rt_list = ShiftAppend(now, Rend-Rstart, Rt_list) 
                    validR = 1
                    TemptoList(validR)
                else:
                    validR = 0
                    TemptoList(validR, Rend-Rstart)
                if PreOverlap != '-':
                    if PreOverlap != MicIn and ((MicIn == 'L' and validR == 1) or (MicIn == 'R' and validL == 1)): #Turn-Change overlap detected, no time constraints given
                        OverlapTemp = [Bend-Bstart,'T']
                        # To_list = ShiftAppend(timestamp, Bend-Bstart, To_list) 
            elif PrevMic == '.':
                if Send-Sstart >= 0.01:    # Beware: Silence detection depends on interval sensitivity settings! (default = 0.01)
                    if PreSilence != '-':
                        duration = Send-Sstart
                        if (PreSilence != MicIn) and ((MicIn == 'L' and validR == 1) or (MicIn == 'R' and validL == 1)): #Possible Turn-Change silence detected
                            SilenceTemp = [duration,'T'] # The valid parameters make sure a new initial silence count is saved after a proper turnperiod     

                        elif (PreSilence == MicIn) and (MicIn == 'L' and validL == 1): # Possible Inter-speech silence detected for the person on the left
                            SilenceTemp = [duration,'L']                            

                        elif (PreSilence == MicIn) and (MicIn == 'R' and validR == 1): # Possible Inter-speech silence detected for the person on the right
                            SilenceTemp = [duration,'R']                            
 
            if MicIn == 'L':
                Lstart = now
            elif MicIn == 'R':
                Rstart = now
            elif MicIn == 'B':
                PreOverlap = PrevMic
                Lstart = now
                Rstart = now
                Bstart = now
            elif MicIn == '.':
                PreSilence = PrevMic
                Sstart = now
        
        PrevMic = MicIn  #Update PrevMic every iteration         
        
        DataOut.LmeanTurnLength =     round(ListMean(Lt_list),2)    #]
        DataOut.LmeanIntervalLength = round(ListMean(Ls_list),2)    #|
        DataOut.LmeanIntervalFreq =   round(len(Ls_list),2)         #|
        DataOut.RmeanTurnLength =     round(ListMean(Rt_list),2)    #|
        DataOut.RmeanIntervalLength = round(ListMean(Rs_list),2)    #| --> Moving window calculation results (not grand total!)
        DataOut.RmeanIntervalFreq =   round(len(Rs_list),2)         #|
        DataOut.turnSilenceTime = round(ListMean(Ti_list),2)        #|
        DataOut.turnSilenceFreq = round(len(Ti_list),2)             #|
        DataOut.turnOverlapTime = round(ListMean(To_list),2)        #|
        DataOut.turnOverlapFreq = round(len(To_list),2)             #]
        DataOut.LturnCount = LturnCnt
        DataOut.RturnCount = RturnCnt
        DataOut.liveWindow = printwindow
        DataOut.LtsRtsTio = getLtsRtsTio([Lt_list, Ls_list, Rt_list, Rs_list, Ti_list, To_list])

    return DataOut
        
def mic_decode(device, in_data, channels):
    """
    Convert a (interleaved) PyAudio byte stream into a 2D numpy array with 
    shape (chunk_size, channels)

    Samples are interleaved, so for a stereo stream with left channel 
    of [L0, L1, L2, ...] and right channel of [R0, R1, R2, ...], the output 
    is ordered as [L0, R0, L1, R1, ...]
    """
    mic = mic_channel()
    
    result = numpy.fromstring(in_data, dtype=numpy.int16)
#    print [int(i) for i in result], len(result)
    chunk_length = len(result) / channels
    assert chunk_length == int(chunk_length)
    result = numpy.reshape(result, (chunk_length, channels))
    if device == 1:
        for i in range(len(result[:, 0])): #apply (add) constant (2000) to one channel (Left) to balance stereo levels USB Mic
                result[[i], 0] += 2000
    elif device == 4:
        for i in range(len(result[:, 0])): #apply (add) constant (422) to one channel (Right) to balance stereo levels USB Line-In
                result[[i], 1] += 422
    else:
        pass
    if channels==1:
        mic.L = mic.R = result[:, 0]
    elif channels==2:
        mic.L = result[:, 0]
        mic.R = result[:, 1]
#    print [int(i) for i in mic.L], len(mic.L)
#    print [int(i) for i in mic.R], len(mic.R)
    return mic

      
def get_rms(shorts):

    # RMS amplitude is defined as the square root of the
    # mean over time of the square of the amplitude.
    
    sum_squares = 0.0         # iterate over the block.
    for sample in shorts:
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n
    RMSvalue = math.sqrt( sum_squares / len(shorts) )

    return RMSvalue

def get_OLRB(StereoChannelList):
    
    if len(StereoChannelList)!=2:
        raise Exception("Make sure a list of length 2n (stereo channels) is given as input")
        
    if   StereoChannelList[0] == 0 and StereoChannelList[1] == 0:
        OLRBout = "."
    elif StereoChannelList[0] != 0 and StereoChannelList[1] == 0:
        OLRBout = "L"
    elif StereoChannelList[0] == 0 and StereoChannelList[1] != 0:
        OLRBout = "R"
    elif StereoChannelList[0] != 0 and StereoChannelList[1] != 0:
        OLRBout = "B"            
    else:
        raise Exception("Only integer values in range [0, >0] are allowed in the input list")

    return OLRBout

def SaveAudio(audio, CHANNELS, RATE, EXIT=0):
    """
    Unfortunately this function does not work for the image shown in the output window "MYWINDOW". 
    It does however work for the unaltered QueryFrame captures (i.e. you save wat the webcam sees),
    which has to be resolved since both the Query-Frame as the Window-image are of type 'cv2.cv.iplimage'...?
    """
    global InitAudiofile
#    global fileframes
    global wavefile
    
    if EXIT == 0 and InitAudiofile:
        now = datetime.datetime.now()
        filename = now.strftime("%Y-%m-%d_%H-%M")+'.wav'
        wavefile = wave.open(filename, 'wb')
        wavefile.setnchannels(CHANNELS)
        wavefile.setsampwidth(pa.get_sample_size(FORMAT))
        wavefile.setframerate(RATE)
        InitAudiofile = False
        
    if EXIT == 0:
        # write the wave
        if wave != None:
#            fileframes.append(wave)
            wavefile.writeframes(audio)
            
    else:
        wavefile.close()
            
def DetectSound(DEVICE_INDEX=0,
                SAMPLERATE = 44100,         # time periods of 0,00002676 s (44.1 samples every 1 millisecond)
                INPUT_BLOCK_TIME = 0.050,   # defined in seconds, this is the audio sequence to be analysed repeatedly
                CHANNELS="stereo", 
                CreateAudioFile = 0,
                voice_threshold = 0.01,     # Default = 0.010 (more sensitive = 0,001)
                intervalbuffer = 3,         # Tweak to filter-out inter-speech silence periods
                peakbuffer = 1,            # Higher number reduces sensitivity for amplitude outliers (spikes)
                WindowSizeSec = 60,         # Dialog calculations are done for samples within a moving window defined in SECONDS.
                resetData = 0):             # To reset dialog data

    global stream    
    global INPUT_SAMPLES_PER_BLOCK
    global ExitAudioFile
    global maxbackground
    global meanbackground
    global stdevbackground
    global noisecount
    global errorcount 
    global speechbuffer
    global initialize
    global calibrationDONE
    global OLRB
    global DialogData
    global amp
    

    if CHANNELS == "stereo":
        CHANNELS = 2
    elif CHANNELS == "mono":
        CHANNELS = 1
    
    if initialize == 0:
        INPUT_SAMPLES_PER_BLOCK = int(SAMPLERATE*INPUT_BLOCK_TIME)
#        for i in range( pa.get_device_count() ): 
        print"Number of active recording devices:", pa.get_device_count()
        sys.stdout.flush()
        for i in range(10):                             #To avoid repetition of device instances only the first 10 (max) are shown
            devinfo = pa.get_device_info_by_index(i)
#            print( "Device %d: %s"%(i,devinfo["name"]) )
            for keyword in ["microphone", "line in", "mic"]:
                if keyword in devinfo["name"].lower():
                    print( "Device %d: %s"%(i,devinfo["name"]) )
                    sys.stdout.flush()

        stream = pa.open(format = FORMAT,                       #]...Pyaudio settings...
                 channels = CHANNELS,                           #|
                 rate = SAMPLERATE,                             #|
                 input = True,                                  #|
                 input_device_index = DEVICE_INDEX,             #|
                 frames_per_buffer = INPUT_SAMPLES_PER_BLOCK)   #]
        
        maxbackground = [0.0,0.0]                   #| The next few variables cover 2 values (one for each channel)
        meanbackground = [0.0,0.0]                  #|
        stdevbackground = [0,0]                     #|
        noisecount = [0,0]                          #|   
        speechbuffer = [0,0]                        #|
        initialize = 1
        ExitAudioFile = CreateAudioFile
    
    if initialize != 0:    
        try:
            block = stream.read(INPUT_SAMPLES_PER_BLOCK)
        except IOError, e:
            print( "Error recording: %s"%(e) )
            sys.stdout.flush()
        
        if CreateAudioFile:
            SaveAudio(block, CHANNELS, SAMPLERATE)
            
        mic_input = mic_decode(DEVICE_INDEX, block, CHANNELS)
        channel_L = get_rms(mic_input.L)
        channel_R = get_rms(mic_input.R)
#        print "L=", channel_L, "R=", channel_R
        for i in range(CHANNELS):
            if i == 0:
                amp[i] = channel_L
            elif i == 1:
                amp[i] = channel_R
            else:
                sys.stdout.write('???')
            if initialize <= CHANNELS:
                maxbackground[i] = meanbackground[i] = amp[i]
                initialize += 1
            elif CHANNELS < initialize <= (1/INPUT_BLOCK_TIME)*CHANNELS: # Samples from first second = determine background noise
                meanbackground[i] = meanbackground[i]*0.5+amp[i]*0.5
                if stdevbackground[i] == 0:
                    stdevbackground[i] = (abs(meanbackground[i]-amp[i]))*0.5
                else:
                    stdevbackground[i] = stdevbackground[i]*0.5+(abs(meanbackground[i]-amp[i]))*0.5
                
                if amp[i] > maxbackground[i]:   # A worst case implementation to maximize voice detection certainty
                    maxbackground[i] = amp[i]   # Could be used at cost of sensitivity (currently it is NOT USED)
                    
                if (1/INPUT_BLOCK_TIME)*CHANNELS-1 <= initialize <= (1/INPUT_BLOCK_TIME)*CHANNELS:
                    print "\nmeanbackground =", meanbackground[i], "stdevbackground =", stdevbackground[i]  
                    sys.stdout.flush()
                initialize += 1              
            else:
                """
                adaptive_voice_threshold = voice_threshold*(1+(25*(amp[i-1]**2)))   # To eliminate inter-channel stereo interference
#                print "\namp[%d] ="%(i), amp[i], "adaptive voice threshold =", adaptive_voice_threshold
#                print "total threshold =", adaptive_voice_threshold+meanbackground[i]+stdevbackground[i], "total-amp[i]=", amp[i]-(adaptive_voice_threshold+meanbackground[i]+stdevbackground[i])
                """
                calibrationDONE = True
                adaptive_voice_threshold = voice_threshold
                
                if abs(i-1)==0: # Determine the amplitude value of the other channel in reference to the current channel
                    other_channel_amp = channel_L # This way both channel values can be used in further processing
#                    sys.stdout.write('Right='+str(channel_R)+'\n')
#                    sys.stdout.write('Right='+str(abs(round(channel_R-meanbackground[i]+stdevbackground[i],3)))+'\n')
                else:
                    other_channel_amp = channel_R
#                    sys.stdout.write('Left='+str(channel_L)+'\t')
#                    sys.stdout.write('Left='+str(abs(round(channel_L-meanbackground[i]+stdevbackground[i],3)))+'    \t')
                
                if (amp[i] > adaptive_voice_threshold+meanbackground[i]+stdevbackground[i]) and (amp[i] > other_channel_amp/2):
                    if noisecount[i] <= peakbuffer:                #                                       /\
                        noisecount[i] += 1                          #                                       |
                    else:                                           # Is to eliminate inter-channel stereo interference
                        pass # noisecount[i] keeps value
                else:
                    noisecount[i] = 0
                    
                    
                if intervalbuffer == 0:
                    if (noisecount[i] > peakbuffer):
                        speechbuffer[i] = 1
                    elif noisecount[i] == 0:
                        speechbuffer[i] = 0
                elif (speechbuffer[i] < intervalbuffer) and (noisecount[i] > peakbuffer):
                    speechbuffer[i] += 1
                elif 0 < speechbuffer[i] and noisecount[i] == 0:
                    speechbuffer[i] -= 1
        
    if calibrationDONE:
        intermediateOLRB = get_OLRB(noisecount)           # This is the direct output without 'peakbuffer' or 'intervalbuffer' influence 
        DialogData = UpdateDialogData(intermediateOLRB, WindowSizeSec, resetData)  # The intermediate value is used to calc. dialog stats
        
        OLRB = get_OLRB(speechbuffer)  # This is the IN-direct 'proper' output with 'peakbuffer' and 'intervalbuffer' taken into account

#        print round(amplitude, 5), round(voice_threshold+(meanbackground+stdevbackground), 5), round(stdevbackground, 5), noisecount, bool(speechbuffer)
    
    return OLRB, DialogData
    
def ExitMicrophone():
    global stream
    global ExitAudioFile
    
    print "Initiating proper closure of microphone script"
    sys.stdout.flush()
    
    # stop stream
    stream.stop_stream()
    stream.close()

    # close PyAudio
    pa.terminate()
    
    if ExitAudioFile == 1:
        SaveAudio(EXIT=1)
    
    print "Microphone script successfully closed"
    sys.stdout.flush()
         