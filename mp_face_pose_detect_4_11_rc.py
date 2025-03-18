# STEP 1: Import the necessary modules.
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import cv2
import math
#from Misty_commands import Misty
import base64
import numpy as np
import matplotlib.pyplot as plt
import datetime
from Misty_commands import getMistyImage, Misty
import threading
import time
class HeadPoseDetect():
    def __init__(self, show_image = False, misty = None):
        self.pitch = 0.0
        self.yaw = 0.0
        self.roll = 0.0
        
        self.is_detecting = False
        self.detector = FaceLandmarker()
        self.cv_cam = None
        self.cv_image = None
        self.show_image = show_image
        self.misty = misty
        self.cv_cam = cv2.VideoCapture(1)
        
    def __del(self):
        if self.is_detecting:
            self.stop_detecting()
        cv2.destroyAllWindows()
        
    def start_detecting(self):
        if self.is_detecting:
            print("Already detecting.")
            return

        self.is_detecting = True

        # Start a new thread for the recording process
        self.thread = threading.Thread(target=self.run_headpose)
        self.thread.start()

    # Stop recording and save the data
    def stop_detecting(self):
        if not self.is_detecting:
            print("Not currently recording.")
            return

        self.is_detecting = False  # Signal to stop recording
        self.thread.join()  # Wait for the recording thread to finish
        
    def log_facepose(self, IDP1, IDP2, head_position_left):
        ct = datetime.datetime.now()
        file_name = "headpose_" + str(IDP1) + '_' + str(IDP2) + ".txt"
        f = open(file_name, 'a')
        f.write(str(head_position_left) + '\t' + str(self.pitch) + '\t' + str(self.yaw) +'\t' + str(ct) + '\t' + '\n')
        f.close()
        
    def run_headpose(self):
        try:
            done = False
            while not done:
                self.detect_headpose()

                if self.show_image:
                    cv2.imshow('Head Pose Angles', self.cv_image)
                    key = cv2.waitKey(100) 
                    if key%256 == 27:
                        # ESC pressed
                        done = True
                else:
                    time.sleep(0.1)

        except Exception as e:
            print(f"An error occurred: {e}")       
    
    def detect_headpose(self):
        if self.misty:
            self.cv_image = cv2.cvtColor(getMistyImage(misty), cv2.COLOR_RGB2BGR)
        else:
            return_value = False
            while not return_value:
                return_value, self.cv_image = self.cv_cam.read()
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=self.cv_image)
        #print("I received the Image in the DetectHeadPose()")
        # STEP 4: Detect face landmarks from the input image.
        detection_result = self.detector.detect(mp_image)

        face_coordination_in_real_world = np.array([
                [285, 528, 200],
                [285, 371, 152],
                [197, 574, 128],
                [173, 425, 108],
                [360, 574, 128],
                [391, 425, 108]
                ], dtype=np.float64)

        h, w, channels = self.cv_image.shape
        face_coordination_in_image = []
        
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence = 0.5, min_tracking_confidence = 0.5)
        results = face_mesh.process(self.cv_image)
        #print("Got the result of the face_mesh processing")

        if results.multi_face_landmarks:
            #print("Face landmarks detected!")
            for face_landmarks in results.multi_face_landmarks:
                #print("I will start the for loop and go through each of the face_landmarks")
                for idx, lm in enumerate(face_landmarks.landmark):
                    if idx in [1, 9, 57, 130, 287, 359]:
                        x, y = int(lm.x * w), int(lm.y * h)
                        face_coordination_in_image.append([x, y])
                        #print("I appended the face_coordination_in_image")

                face_coordination_in_image = np.array(face_coordination_in_image,
                                                        dtype=np.float64)

                # The camera matrix
                focal_length = 1 * w
                cam_matrix = np.array([[focal_length, 0, w / 2],
                                        [0, focal_length, h / 2],
                                        [0, 0, 1]])

                # The Distance Matrix
                dist_matrix = np.zeros((4, 1), dtype=np.float64)

                # Use solvePnP function to get rotation vector
                success, rotation_vec, transition_vec = cv2.solvePnP(
                    face_coordination_in_real_world, face_coordination_in_image,
                    cam_matrix, dist_matrix)
                #print("I have succesfully solved the matrix")

                # Use Rodrigues function to convert rotation vector to matrix
                rotation_matrix, jacobian = cv2.Rodrigues(rotation_vec)

                result = rotation_matrix_to_angles(rotation_matrix)
                
                #Print results of pitch and yaw
                self.pitch, self.yaw, self.roll = result[0], result[1], result[2]
                #print(f'Pitch: {self.pitch:.2f} degrees, Yaw: {self.yaw:.2f} degrees')
                
                if self.show_image:
                    # # Show picture
                    for i, info in enumerate(zip(('pitch', 'yaw', 'roll'), result)):
                        k, v = info
                        text = f'{k}: {int(v)}'
                        cv2.putText(self.cv_image, text, (20, i*30 + 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 0, 200), 2)


                # # STEP 5: Process the detection result. In this case, visualize it.
                    self.cv_image = draw_landmarks_on_image(self.cv_image, detection_result)
                    
                        
            return self.pitch, self.yaw, self.roll    




   



def draw_landmarks_on_image(rgb_image, detection_result):
  face_landmarks_list = detection_result.face_landmarks
  annotated_image = np.copy(rgb_image)

  # Loop through the detected faces to visualize.
  for idx in range(len(face_landmarks_list)):
    face_landmarks = face_landmarks_list[idx]

    # Draw the face landmarks.
    face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    face_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in face_landmarks
    ])

    solutions.drawing_utils.draw_landmarks(
        image=annotated_image,
        landmark_list=face_landmarks_proto,
        connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp.solutions.drawing_styles
        .get_default_face_mesh_tesselation_style())
    solutions.drawing_utils.draw_landmarks(
        image=annotated_image,
        landmark_list=face_landmarks_proto,
        connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp.solutions.drawing_styles
        .get_default_face_mesh_contours_style())
    solutions.drawing_utils.draw_landmarks(
        image=annotated_image,
        landmark_list=face_landmarks_proto,
        connections=mp.solutions.face_mesh.FACEMESH_IRISES,
          landmark_drawing_spec=None,
          connection_drawing_spec=mp.solutions.drawing_styles
          .get_default_face_mesh_iris_connections_style())

  return annotated_image

def plot_face_blendshapes_bar_graph(face_blendshapes):
  # Extract the face blendshapes category names and scores.
  face_blendshapes_names = [face_blendshapes_category.category_name for face_blendshapes_category in face_blendshapes]
  face_blendshapes_scores = [face_blendshapes_category.score for face_blendshapes_category in face_blendshapes]
  # The blendshapes are ordered in decreasing score value.
  face_blendshapes_ranks = range(len(face_blendshapes_names))

  fig, ax = plt.subplots(figsize=(12, 12))
  bar = ax.barh(face_blendshapes_ranks, face_blendshapes_scores, label=[str(x) for x in face_blendshapes_ranks])
  ax.set_yticks(face_blendshapes_ranks, face_blendshapes_names)
  ax.invert_yaxis()

  # Label each bar with values
  for score, patch in zip(face_blendshapes_scores, bar.patches):
    plt.text(patch.get_x() + patch.get_width(), patch.get_y(), f"{score:.4f}", va="top")

  ax.set_xlabel('Score')
  ax.set_title("Face Blendshapes")
  plt.tight_layout()
  plt.show()

def FaceLandmarker():
    # STEP 2: Create an FaceLandmarker object.
    base_options = python.BaseOptions(model_asset_path='face_landmarker_v2_with_blendshapes.task')
    options = vision.FaceLandmarkerOptions(base_options=base_options,
                                           output_face_blendshapes=True,
                                           output_facial_transformation_matrixes=True,
                                           num_faces=1)
    detector = vision.FaceLandmarker.create_from_options(options)
    return detector

def rotation_matrix_to_angles(rotation_matrix):
    """
    Calculate Euler angles from rotation matrix.
    :param rotation_matrix: A 3*3 matrix with the following structure
    [Cosz*Cosy  Cosz*Siny*Sinx - Sinz*Cosx  Cosz*Siny*Cosx + Sinz*Sinx]
    [Sinz*Cosy  Sinz*Siny*Sinx + Sinz*Cosx  Sinz*Siny*Cosx - Cosz*Sinx]
    [  -Siny             CosySinx                   Cosy*Cosx         ]
    :return: Angles in degrees for each axis
    """
    x = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
    y = math.atan2(-rotation_matrix[2, 0], math.sqrt(rotation_matrix[0, 0] ** 2 +
                                                     rotation_matrix[1, 0] ** 2))
    z = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
    return np.array([x, y, z]) * 180. / math.pi           

 
if __name__ == "__main__":
    misty = Misty(ip_address="192.168.0.100")
    hpdetector  = HeadPoseDetect(show_image=False)
    
    hpdetector.start_detecting()
    t0=time.time()
    t1=t0
    while t1-t0 < 10:
        print(hpdetector.pitch, hpdetector.yaw)
        t1=time.time()
    hpdetector.stop_detecting()
    
    input("test phase 2")
    print("Main loop is started")
    done = False
    try:
        while not done:
            hpdetector.detect_headpose()

            if hpdetector.show_image:
                cv2.imshow('Head Pose Angles', hpdetector.cv_image)
                key = cv2.waitKey(100) 
                if key%256 == 27:
                    # ESC pressed
                    done = True

    except Exception as e:
        print(f"An error occurred: {e}")