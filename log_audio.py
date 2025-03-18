import AVData
from Misty_commands import Misty
import msvcrt

def main():
    log_data = AVData.AVData()
    robot_ip = "192.168.0.100"
    misty = Misty(ip_address=robot_ip)
    log_data.init_robot(robot_ip)
    log_data.init_devices()
    print("Press button 's' to start recording, 't' to stop logging")
    pressedButton = 's'
    while pressedButton != "t":
        pressedButton = msvcrt.getch().decode('ASCII')
        if pressedButton == "s":
            log_data.start_logging_data()
    else: 
        log_data.stop_logging_data()

if __name__ == "__main__":
    main()