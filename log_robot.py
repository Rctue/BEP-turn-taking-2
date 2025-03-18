# Add mistyPy directory to sys path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mistyPy.Robot import Robot
from mistyPy.Events import Events
from mistyPy.EventFilters import EventFilters
from time import time, sleep, strftime
import csv

writer = None
f = None
misty_robot = None
   

def register_events():
    global misty_robot
    
    try:
        # Subscribe to the tofs individually so each message from each tof is written to a new line
        # class ActuatorPosition(object):
        # ArmLeft = event_filter("SensorId", "=", "ala")
        # ArmRight = event_filter("SensorId", "=", "ara")
        # HeadPitch = event_filter("SensorId", "=", "ahp")
        # HeadRoll = event_filter("SensorId", "=", "ahr")
        # HeadYaw = event_filter("SensorId", "=", "ahy")
        
        pitch = misty_robot.RegisterEvent("pitch", Events.ActuatorPosition, condition=[EventFilters.ActuatorPosition.HeadPitch], keep_alive=True, callback_function=log_headpose_reading, debounce=5)
        roll = misty_robot.RegisterEvent("roll", Events.ActuatorPosition, condition=[EventFilters.ActuatorPosition.HeadRoll], keep_alive=True, callback_function=log_headpose_reading, debounce=5)
        yaw = misty_robot.RegisterEvent("yaw", Events.ActuatorPosition, condition=[EventFilters.ActuatorPosition.HeadYaw], keep_alive=True, callback_function=log_headpose_reading, debounce=5)
         
    except Exception as ex:
        print(ex)
    
def log_headpose_reading(message):
    global writer
    
    headpose_message = message["message"]
    #print(headpose_message)
    if writer !=None:
        writer.writerow([headpose_message['created'][:-1].replace('T',' '),headpose_message['sensorId'],headpose_message['value']])


def start_logging():
    global f, writer
    
    timestr = strftime("-%Y%m%d-%H%M%S")
    f = open(f"log_robot_{timestr}.csv", "w", newline='')
    writer = csv.writer(f, delimiter = '\t')
    writer.writerow(["time","sensor_id","value"])
    
    register_events()
    
def stop_logging():
    global f, misty_robot
    
    f.close()
    
    # Unregister from all events or the spawned threads won't get killed
    misty_robot.UnregisterAllEvents()
       
if __name__ == "__main__":
    ROBOT_IP = "192.168.0.100"
    misty_robot = Robot(ROBOT_IP)


    start_logging()
    
    # Use the keep_alive() function if you want to keep the main thread alive, otherwise the event threads will also get killed once processing has stopped
    #misty_robot.keep_alive()
    sleep(3)
    stop_logging()
