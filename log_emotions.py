import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg" # for linux/mac os

#pip install fer
from fer import FER # use pip install fer
import cv2

emotion_detector = FER(mtcnn=True)

def detect_emotions(cv_image, show_image = False):
    analysis = emotion_detector.detect_emotions(cv_image)
    face_data = []
    for face in analysis:
        fb=face['box']
        top_left = [fb[0],fb[1]]
        bottom_right = [fb[0]+fb[2],fb[1]+fb[3]]
        face_center = [fb[0]+fb[2]/2.0,fb[1]+fb[3]/2.0]
        
        
        if show_image:
            cv2.rectangle(cv_image,top_left,bottom_right,(0,0,255),2) # red color, thickness 2 points
        
        k=list(face['emotions'].keys())
        v=list(face['emotions'].values())
        emotion_score = max(v)
        dominant_emotion = k[v.index(emotion_score)]
        
        if show_image:
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(cv_image,dominant_emotion+' '+str(emotion_score),(top_left[0],top_left[1]-10), font, 0.4,(0,0,255),1,cv2.LINE_AA) #scale is 0.4, red color, 1 point thick
        
        face_data.append(face_center + fb + [ dominant_emotion, emotion_score ])
          
    if show_image:
        cv2.imshow("multiple faces", cv_image)
        cv2.waitKey(0)
        cv2.destroyWindow("multiple faces")
        
    return face_data
    
if __name__=="__main__":
    cv_image = cv2.imread("multiple_faces.png")

    face_data = detect_emotions(cv_image, True)
    
    camera = cv2.VideoCapture(1)
    cv2.namedWindow("cam feed")
    done = False
    while not done:
        return_value, cv_image = camera.read()
        if not return_value:
            break
        else:
            dominant_emotion, emotion_score = emotion_detector.top_emotion(cv_image)
            if dominant_emotion == None:
                dominant_emotion = "None"
            print(dominant_emotion, emotion_score)
            cv2.putText(cv_image, dominant_emotion + ' ' + str(emotion_score),(50,50), font, 2,(0,0,255),2,cv2.LINE_AA) #scale is 0.4, red color, 1 point thick
            cv2.imshow("cam feed", cv_image)
            k = cv2.waitKey(1)
            if k%256 == 27:
                # ESC pressed
                done = True
                break
            
    cv2.destroyWindow("cam feed")
    

    test_img_low_quality = cv2.imread("low_quality_emotion.png")
    dominant_emotion, emotion_score = emotion_detector.top_emotion(test_img_low_quality)
    print(dominant_emotion, emotion_score)

    cv2.putText(test_img_low_quality, dominant_emotion + ' ' + str(emotion_score),(10,10), font, 0.4,(0,0,255),1,cv2.LINE_AA) #scale is 0.4, red color, 1 point thick
    cv2.imshow("low quality image", test_img_low_quality)
    cv2.waitKey(0)
    cv2.destroyWindow("low quality image")


