import matplotlib.pyplot as plt
import numpy as np
import wave

file = 'output.wav'

def calculate_rms(audio_data):
    rms = np.sqrt(np.mean(np.square(np.asarray(audio_data, dtype=float)),axis=1))/32768.0
    return rms

def calculate_rms_dbA(audio_data):
    rms_dbA = 20*np.log10(calculate_rms(audio_data))
    return rms_dbA

with wave.open(file,'r') as wav_file:
    #Extract Raw Audio from Wav File
    signal = wav_file.readframes(-1)
    signal = np.fromstring(signal, dtype=np.int16)
    
    #Split the data into channels 
    channels = [[] for channel in range(wav_file.getnchannels())]
    for index, datum in enumerate(signal):
        channels[index%len(channels)].append(datum)

    print("RMS in dbA: " + str(calculate_rms_dbA(channels)))
    
    #Get time from indices
    fs = wav_file.getframerate()
    Time=np.linspace(0, len(signal)/len(channels)/fs, num=int(len(signal)/len(channels)))

    #Plot
    plt.figure(1)
    plt.title('Signal Wave...')
    for channel in channels:
        plt.plot(Time,np.divide(channel,32768.0))
    plt.show()
    
    plt.figure(1)
    plt.title('RMS Wave...')
    plt.plot(Time,np.square(np.divide(np.mean(channels, axis=0),32768.0)))
    plt.show()