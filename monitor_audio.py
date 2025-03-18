# Monitor audio routines
import Audio_sound_levels as au
import time
import matplotlib.pyplot as plt

# def get_OLRB(StereoChannelList):
    
#     if len(StereoChannelList)!=2:
#         raise Exception("Make sure a list of length 2n (stereo channels) is given as input")
        
#     if   StereoChannelList[0] == 0 and StereoChannelList[1] == 0:
#         OLRBout = "."
#     elif StereoChannelList[0] != 0 and StereoChannelList[1] == 0:
#         OLRBout = "L"
#     elif StereoChannelList[0] == 0 and StereoChannelList[1] != 0:
#         OLRBout = "R"
#     elif StereoChannelList[0] != 0 and StereoChannelList[1] != 0:
#         OLRBout = "B"            
#     else:
#         raise Exception("Only integer values in range [0, >0] are allowed in the input list")

#     return OLRBout


# def silentfor(AVInput, sec=0):
#     global initA
#     global t1
#     global t2
#     MeanSystemDelay = 0.5
    
#     signal = False
#     if AVInput.mic != "-":   
#         if initA == 0 and AVInput.mic == ".":
#             time_c = time.clock()
#             t1 = time_c
#             t2 = time_c
#             initA = 1
            
#         elif initA == 1 and AVInput.mic == ".":
#             t2 = time.clock()

#         else:
#             time_c = time.clock()
#             t1 = time_c
#             t2 = time_c
#             #print "sound faaal"
            
#         t_diff = t2-t1    
        
#         if initA == 1 and t_diff >= sec-MeanSystemDelay:
#             signal = True
#             #initA = 0 
#             #print "t_diff WINNAAAR =", t_diff
#         else:
#             signal = False
        
#         #print "t_diff, signal =", t_diff, signal
#     return signal


if __name__=="__main__":
    rec1 = au.AudioRecorder(input_device = 1)
    rec1.calibrate()
    
    rec1.start_recording()
    
    total_silence_data=[]
    silence_data=[]
    speech_data=[]
    for i in range(100):
        print(rec1.total_silence_duration, rec1.silence_duration, rec1.speaking_duration)
        total_silence_data.append(rec1.total_silence_duration)
        silence_data.append(rec1.silence_duration)
        speech_data.append(rec1.speaking_duration)
        time.sleep(0.05)
        
    rec1.stop_recording()
    
    plt.plot(silence_data,'r')
    plt.plot(speech_data,'g')
    plt.plot(total_silence_data,'b')
    plt.legend(['silence duration', 'speech_duration', 'total silence'])
    plt.show()
    