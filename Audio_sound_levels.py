import pyaudio
import wave
import csv
import numpy as np
import threading
import time
import matplotlib.pyplot as plt

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

class AudioRecorder:
    def __init__(self, input_device = 39, format=pyaudio.paInt16, channels=1, rate=44100, chunk=1024, verbose = False):
        self.input_device = input_device
        self.audio = pyaudio.PyAudio()
        self.device = self.audio.get_device_info_by_index(self.input_device)
        # ### Example output for audio device
        #  {'index': 0, 'structVersion': 2, 'name': 'Microsoft Sound Mapper - Input', 'hostApi': 0, 'maxInputChannels': 2, 'maxOutputChannels': 0,
        #  'defaultLowInputLatency': 0.09, 'defaultLowOutputLatency': 0.09, 'defaultHighInputLatency': 0.18, 'defaultHighOutputLatency': 0.18, 
        # 'defaultSampleRate': 44100.0}
        self.CHANNELS = self.device['maxInputChannels']  
        self.RATE = int(self.device['defaultSampleRate'] )
        
        self.FORMAT = format 
        self.CHUNK = chunk
        self.verbose = verbose
        self.OUTPUT_FILENAME = None

        self.frames = []
        self.rms_data = []
        self.wave_data = []
        self.is_recording = False
        self.stream = None

        self.thread = None
        self.speech_threshold = 0.20  # Adjust this according to what the threshold seems to be for speaking
        #self.silence_buffer_size  = 10 # length of silence buffer
        
        self.silence_duration = 0.0
        self.total_silence_duration = 0.0
        self.speaking_duration = 0.0
        self.total_speaking_duration = 0.0
        self.start_speech_time = None
        self.start_silence_time = None
        
        self.is_above_threshold = False
        self.calibrated = False
        
        #self.initE = 0
        #self.tx = 0
        #self.ty = 0

    def __del__(self):
        self.terminate()
        
    # Function to calculate RMS (Root Mean Square) of audio data
    def calculate_rms(self, audio_data):
        SHORT_NORMALIZE = (1.0/32768.0) # 16-bit == 65536 == +-32768 (one bit is used as sign)

        audio_data = np.asarray(np.frombuffer(audio_data, dtype=np.int16), dtype=float)*SHORT_NORMALIZE*100.0 # in percent of max amplitude
        if self.CHANNELS>1:
            # channels are interleaved e.g. for stereo CHANNELS=2 and 
            # data are stored as: [c0s0, c1s0, c0s1, c1s1, c0s2, c1s2, ...]
            # - reshape splits interleaved data into column vectors  
            # - mean takes averag of all channels 
            audio_data = np.mean(audio_data.reshape(-1,self.CHANNELS), axis = 1)
        
        # to compute rms the mean across all squared samples is taken, followed by sqrt()
        rms = np.sqrt(np.mean(np.square(audio_data)))
        return rms

    def calibrate(self):
        done = False
        while not done:
            input("Record 3s silence uisng {}. Press enter when ready".format(self.device['name']))
            self.start_recording()
            time.sleep(3)
            self.stop_recording()
            silence = np.median(self.rms_data)
            print("Median rms value of silence is " + str(silence))
            
            input("Record 3s of speech uisng {}. Press enter when ready".format(self.device['name']))
            self.start_recording()
            time.sleep(3)
            self.stop_recording()
            speech = np.max(self.rms_data)
            print("Max rms value of speech is " + str(speech) + "Median rms value of silence is " + str(silence))
            
            if speech < silence*3: # 2 would mean that max speech level is equal to median silence level, so better 3
                print("Speech is not loud enough.")
            else:
                self.speech_threshold = silence*2
                print("Speech is loud enough. Keeping new threshold {}".format(self.speech_threshold))
                
            
            res = input("Do you want to try again? (y/n)")
            if res.lower() != 'y':
                    done = True
        
        
    # Start recording and measuring sound levels
    def start_recording(self):
        if self.is_recording:
            print("Already recording.")
            return

        self.is_recording = True
        self.frames = []  # Reset frames list
        self.rms_data = []
        self.wave_data = []
        self.speaking_duration = 0.0
        self.silence_duration = 0.0
        self.total_speaking_duration = 0.0
        self.total_silence_duration = 0.0
        self.start_speech_time = None
        self.start_silence_time = None
        
        self.stream = self.audio.open(input_device_index=self.input_device, format=self.FORMAT, channels=self.CHANNELS,
                                      rate=self.RATE, input=True,
                                      frames_per_buffer=self.CHUNK)

        print("Recording from {} started...".format(self.device['name']))

        # Start a new thread for the recording process
        self.thread = threading.Thread(target=self.record_audio)
        self.thread.start()

    # Stop recording and save the data
    def stop_recording(self):
        if not self.is_recording:
            print("Not currently recording.")
            return

        self.is_recording = False  # Signal to stop recording
        self.thread.join()  # Wait for the recording thread to finish

        # Stop and close the stream
        self.stream.stop_stream()
        self.stream.close()

        print("Recording stopped.")
        self.wave_data = b''.join(self.frames)
        
    def save_data(self, output_filename="output.wav"):
            # Save the recorded data as a WAV file
            self.OUTPUT_FILENAME = output_filename
            wf = wave.open(self.OUTPUT_FILENAME, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(self.wave_data)
            wf.close()
            print(f"File saved as {self.OUTPUT_FILENAME}")

    def save_rms_data(self, output_filename="rms_data.csv"):
            # Save the recorded data as a WAV file
            with open(output_filename, 'w', newline='') as f:
                writer = csv.writer(f, delimiter = '\t')
                writer.writerows(np.array([list(range(len(self.rms_data))),self.rms_data]).T)
                print(f"RMS data saved as {output_filename}")

    # Function that records audio in chunks and measures sound levels
    def record_audio(self):
        while self.is_recording:
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)

            
            # Calculate and display sound level (RMS)
            rms_value = self.calculate_rms(data)
            self.rms_data.append(rms_value)
            if self.verbose:
                if rms_value > 0:
                    print(f"Sound Level (RMS): {rms_value:.2f} | {'*' * int(rms_value * 10)}")
                else:
                    print("No sound detected or too much sound detected.")

            
            # Update continuous speaking duration based on threshold
            delta_t = 1.0/self.RATE*self.CHUNK
            if rms_value > self.speech_threshold:
                self.is_above_threshold = True
                self.total_speaking_duration +=delta_t
                self.speaking_duration += delta_t
                self.silence_duration =0
            else:
                self.is_above_threshold = False
                self.total_silence_duration +=delta_t
                self.silence_duration +=delta_t
                self.speaking_duration =0
                
                
            # #More elaborate time keeping but does not result in better data
            # if rms_value > self.speech_threshold:
            #     if not self.is_above_threshold:
            #         self.is_above_threshold = True
            #         self.start_speech_time = time.time()
            #     self.total_speaking_duration +=delta_t
            #     if self.start_speech_time is not None:
            #         self.speaking_duration = time.time() - self.start_speech_time # +=delta_t
            #     else:
            #         self.speaking_duration += delta_t
            #     self.silence_duration =0
                
            # else:
            #     if self.is_above_threshold:
            #         self.is_above_threshold = False
            #         self.start_silence_time = time.time()
            #     self.total_silence_duration +=delta_t
            #     if self.start_silence_time is not None:
            #         self.silence_duration = time.time() - self.start_silence_time
            #     else:
            #         self.silence_duration += delta_t
            #     self.speaking_duration =0
            

        if self.verbose:
            print(f"Continuous speaking duration: {self.speaking_duration:.2f} seconds")
            print(f"Total silence duration: {self.silence_duration:.2f} seconds")
            

        return self.speaking_duration, self.silence_duration

        
    # Clean up the PyAudio object
    def terminate(self):
        if self.is_recording:
            self.is_recording = False  # Signal to stop recording
            self.thread.join()  # Wait for the recording thread to finish

            # Stop and close the stream
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
        print("Audio terminated.")

if __name__ == "__main__":
    dev_list = list_devices(False)
    for dev in dev_list:
        if dev['maxInputChannels']>0 and dev['defaultSampleRate']==44100:
            print(dev['index'], dev['name'], 'Inputs: ', dev['maxInputChannels'])
    mydevice = int(input("Choose input device from list: "))
    
    all_input_devices = [[dev['index'], dev['name']] for dev in dev_list if dev['maxInputChannels']>0 and dev['defaultSampleRate']==44100]
    #print(all_input_devices)



    # Create an instance of AudioRecorder
    recorder = AudioRecorder( input_device = mydevice, verbose = True)
    recorder.calibrate()
    # Start recording
    recorder.start_recording()

    # Recording for 20 seconds
    time.sleep(3)
    
    # Stop recording
    recorder.stop_recording()
    recorder.save_data()
    recorder.save_rms_data()
    
    #Plot
    plt.figure(1)
    plt.title('Signal Wave...')
    channel_data = np.asarray(np.frombuffer(recorder.wave_data, dtype=np.int16), dtype=float).reshape((-1,recorder.CHANNELS))
    for c in channel_data.T:
        plt.plot(c)
    plt.show()
    
    plt.plot(recorder.rms_data)
    plt.show()

    # Terminate PyAudio when done
    recorder.terminate()