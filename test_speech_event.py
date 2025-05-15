from time import time, sleep, strftime
import csv
from mistyPy.Robot import Robot
from mistyPy.Events import Events
from mistyPy.EventFilters import EventFilters

misty_robot = None
start_time = 0   

def register_events():
    global misty_robot
    
    try:
        # Subscribe to the tofs individually so each message from each tof is written to a new line
        # class ActuatorPosition(object):
        
        text_complete = misty_robot.RegisterEvent("text", Events.TextToSpeechComplete, keep_alive=True, callback_function=cb_text_complete, debounce=5)
        #pitch = misty_robot.register_event("pitch", Events.ActuatorPosition, condition=[EventFilters.ActuatorPosition.HeadPitch], keep_alive=True, callback_function=cb_text_complete, debounce=5)
        print(text_complete)
    except Exception as ex:
        print(ex)
    
def cb_text_complete(data):
    global writer, start_time
    print(data["message"])
    print(time()-start_time, data["message"])
    # headpose_message = message["message"]
    # #print(headpose_message)
    # if writer !=None:
    #     writer.writerow([headpose_message['created'][:-1].replace('T',' '),headpose_message['sensorId'],headpose_message['value']])


def start_logging():
    global f, writer, start_time
    
    timestr = strftime("-%Y%m%d-%H%M%S")
    f = open(f"log_speech_{timestr}.csv", "w", newline='')
    writer = csv.writer(f, delimiter = '\t')
    writer.writerow(["time","sensor_id","value"])
    
    start_time = time()
    register_events()
    
def stop_logging():
    global f, misty_robot
    
    f.close()
    
    # Unregister from all events or the spawned threads won't get killed
    misty_robot.UnregisterAllEvents()
       
if __name__ == "__main__":
    ROBOT_IP = "192.168.0.102"
    misty_robot = Robot(ROBOT_IP)


    start_logging()
    
    # Use the keep_alive() function if you want to keep the main thread alive, otherwise the event threads will also get killed once processing has stopped
    #misty_robot.keep_alive()
    misty_robot.Speak("Hello",utteranceId = "id_hello")
    sleep(1)
    misty_robot.Speak("how are you?")
    sleep(3)
    stop_logging()
