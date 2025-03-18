import Audio_sound_levels as au
import log_robot
import time

class AVData():
    def __init__(self):
        self.rec1 = None
        self.rec2 = None
        self.is_logging = False
        
        self.robot = None
        
        self.experiment_data = {}
    
    def __del__(self):
        if self.rec1 is not None:
            del self.rec1
            self.rec1 = None
        if self.rec2 is not None:
            del self.rec2
            self.rec2 = None
            
    
    def init_devices(self):
        dev_list = au.list_devices(False)
        for dev in dev_list:
            if dev['maxInputChannels']>0 and dev['defaultSampleRate']==44100:
                print(dev['index'], dev['name'], 'Inputs: ', dev['maxInputChannels'])
        self.device1 = int(input("Choose FIRST (left) input device from list: "))
        self.device2 = int(input("Choose SECOND (right) input device from list: "))

        self.rec1 = au.AudioRecorder(input_device=self.device1)
        self.rec2 = au.AudioRecorder(input_device=self.device2)
        
        print("Calibrate FIRST (left) input device")
        self.rec1.calibrate()
        print("Calibrate SECONG (right) input device")
        self.rec2.calibrate()
        
        
        
    def init_robot(self, robot_ip):
        log_robot.misty_robot = log_robot.Robot(robot_ip)
        self.robot = log_robot.misty_robot
        
    def start_logging_data(self):
        self.is_logging = True
        self.rec1.start_recording()
        self.rec2.start_recording()
        
        if self.robot != None:
            log_robot.start_logging()
        

    def stop_logging_data(self):
        self.rec1.stop_recording()
        self.rec2.stop_recording()
        
        timestr = time.strftime("-%Y%m%d-%H%M%S")
        self.rec1.save_rms_data(f"rms_data_{self.experiment_data['condition']}_{self.experiment_data['topic']}_{self.experiment_data['gestures']}_{self.experiment_data['IDP1']}_{timestr}.csv")
        self.rec2.save_rms_data(f"rms_data_{self.experiment_data['condition']}_{self.experiment_data['topic']}_{self.experiment_data['gestures']}_{self.experiment_data['IDP2']}_{timestr}.csv")
        self.is_logging = False

        if self.robot != None:
            log_robot.stop_logging() # also saves data

if __name__=="__main__":
    av_data = AVData()
    av_data.init_devices()
    av_data.init_robot('192.168.0.100')
    av_data.experiment_data = {'condition':'h', 'topic': 'h', 'gestures': 'y', 'IDP1': 1, 'IDP2': 2}

    av_data.start_logging_data()
    
    time.sleep(3)
    
    av_data.stop_logging_data()


        
        