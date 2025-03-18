from Misty_commands import Misty
import cv2
import base64
import numpy as np

def list_all_images(misty):
    result = misty.get_image_list().json()["result"]
    for r in result:
        print(r)
    
def getMistyImage(misty):
    result = misty.take_picture(base64 = True, fileName = "TempImage01", width = 800, height = 600, displayOnScreen = False, overwriteExisting = True)
    if (result.json()['status'] == "Success"):
        returnvalue = True
        result = misty.get_image(fileName = "TempImage01.jpg", base64 = True)
        image = result.json()['result']['base64']  # raw data with base64 encoding
        decoded_data = base64.b64decode(image)
        np_data = np.fromstring(decoded_data,np.uint8)
        img = cv2.imdecode(np_data,cv2.IMREAD_UNCHANGED)

    else:
        returnvalue = False
        img = None
    return returnvalue, img

if __name__=="__main__":
    misty = Misty(ip_address="192.168.0.103")
    
    list_all_images(misty)
    
    done = False
    while not done:
        returnval, img = getMistyImage(misty)
        if returnval:      
            cv2.imshow("test", img)
            key=cv2.waitKey(1)
            if key%256==27: #escape key
                done = True
    cv2.destroyWindow("test")