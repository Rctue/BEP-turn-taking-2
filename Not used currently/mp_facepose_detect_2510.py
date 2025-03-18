#!pip install mediapipe
# also needs opencv, numpy, matplotlib

# # STEP 1: Import the necessary modules.
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import math
from Misty_commands import Misty
import base64

# STEP 1B: viusalisation tools
# #@markdown We implemented some functions to visualize the face landmark detection results. <br/> Run the following cell to activate the functions.

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import matplotlib.pyplot as plt
from Misty_commands import Misty

misty = Misty(ip_address="192.168.0.103")

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

def DetectHeadPose(cv_image, detector):
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv_image)
    # STEP 4: Detect face landmarks from the input image.
    detection_result = detector.detect(image)
    return detection_result, image 

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

def main():
    detector = FaceLandmarker()        
    # STEP 3: Load the input image.
    
    camera = cv2.VideoCapture(0) # Elke keer een image inladen en dan 
    im_name = "Head Pose Estimation Including Pitch And Yaw"
    done = False
    while not done:
        # I do not know how to input the camera of the robot Misty now
        return_value, cv_image = camera() #getMistyImage(misty)
        if return_value:
            detection_result, image = DetectHeadPose(cv_image, detector)
            face_coordination_in_real_world = np.array([
                [285, 528, 200],
                [285, 371, 152],
                [197, 574, 128],
                [173, 425, 108],
                [360, 574, 128],
                [391, 425, 108]
                ], dtype=np.float64)

        h = 1200
        w= 1600
        face_coordination_in_image = []
        
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence = 0.5, min_tracking_confidence = 0.5)
        results = face_mesh.process(image)
    
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for idx, lm in enumerate(face_landmarks.landmark):
                    if idx in [1, 9, 57, 130, 287, 359]:
                        x, y = int(lm.x * w), int(lm.y * h)
                        face_coordination_in_image.append([x, y])
    
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
    
                # Use Rodrigues function to convert rotation vector to matrix
                rotation_matrix, jacobian = cv2.Rodrigues(rotation_vec)
    
                result = rotation_matrix_to_angles(rotation_matrix)
                
                #Print results of pitch and yaw
                pitch, yaw, roll = result[0], result[1], result[2]
                print(f'Pitch: {pitch:.2f} degrees, Yaw: {yaw:.2f} degrees')
                head_position = Misty.get_head_position()
                print(head_position)
                    
                # Show picture
                for i, info in enumerate(zip(('pitch', 'yaw', 'roll'), result)):
                    k, v = info
                    text = f'{k}: {int(v)}'
                    cv2.putText(image, text, (20, i*30 + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 0, 200), 2)
    
    
            #cv2.imshow('Head Pose Angles', cv_image)
            # STEP 5: Process the detection result. In this case, visualize it.
            annotated_image = draw_landmarks_on_image(image, detection_result)
            cv2.imshow(im_name, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
           # cv2.imshow(im_name, cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR))
            key = cv2.waitKey(100)
            if key%256 == 27:
                # ESC pressed
                done = True
                break
    cv2.destroyWindow(im_name)
    # How should I ensure that if I have these Pitch and Yaw numbers that these will be given to the main file Experiment code?
    
if __name__ == "__main__":
    main()