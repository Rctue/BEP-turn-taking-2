import pyaudio
import wave
import sys
import numpy as np

def list_devices(verbose = False):
    p = pyaudio.PyAudio()
    
    device_list=[]
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        device_list.append(dev)
        if verbose:
            print(f"Index: {dev['index']} {dev['name']}\t Inputs: {dev['maxInputChannels']}\t Outputs: {dev['maxOutputChannels']}\t SampleRate: {dev['defaultSampleRate']}")
        
    p.terminate()
    return device_list

def record_from_device(input_device=None,  RECORD_SECONDS = 5, CHANNELS = 1, RATE=44100 ):
    """PyAudio Example: Record a few seconds of audio and save to a wave file."""

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    #CHANNELS = 1 if sys.platform == 'darwin' else 2
    #RATE = 44100
    #RECORD_SECONDS = 5

    with wave.open('output.wav', 'wb') as wf:
        p = pyaudio.PyAudio()
        
        stream = p.open(input_device_index=input_device, format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

        print('Recording...')
        frames = []
        for _ in range(0, RATE // CHUNK * RECORD_SECONDS):
            data = stream.read(CHUNK)
            frames.append(data)
        stream.close()
        p.terminate()
        
        print('Writing data')
        all_frames = b''.join(frames)
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(all_frames)
        wf.close()
        
        print('Done')

        rms = calculate_rms(all_frames)
        return rms, np.frombuffer(all_frames, dtype=np.int16)
    
    
def calculate_rms(audio_data):
    audio_data = np.frombuffer(audio_data, dtype=np.int16)
    rms = np.sqrt(np.mean(np.square(audio_data)))
    return rms
        
if __name__=="__main__":
    dev_list = list_devices(verbose = True)
    
    for dev in dev_list:
        if dev["maxInputChannels"]>=1:
            ans = input("Record from " + dev["name"] + "? [Y/N] ")
            if ans.lower()=="y":
                rms, audio_data = record_from_device(dev["index"], RECORD_SECONDS=5, RATE=int(dev["defaultSampleRate"]), CHANNELS = dev["maxInputChannels"])
                print('rms: '+str(rms))
                print(rms.shape, audio_data.shape)
    
    
    