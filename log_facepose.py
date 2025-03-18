from mp_face_pose_detect_19_11 import get_pitch_yaw
import datetime
import msvcrt
from Misty_commands import Misty

misty = Misty(ip_address = "192.168.0.100")

IDP1 = input("ID participant 1: ")
IDP2 = input("ID participant 2: ")

def log_facepose():
    pitch, yaw = get_pitch_yaw()
    ct = datetime.datetime.now()
    file_name = "headpose_" + str(IDP1) + '_' + str(IDP2) + ".txt"
    f = open(file_name, 'a')
    f.write(str(pitch) + '\t' + str(yaw) +'\t' + str(ct) + '\t' + '\n')
    f.close()

def main():
    pressedButton = 's'
    pressedButton = msvcrt.getch().decode('ASCII')
    while pressedButton != 't':
        log_facepose()
    else: 
        quit()

if __name__ == "__main__":
    log_facepose()