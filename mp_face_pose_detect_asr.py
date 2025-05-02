# Explanation:
# Pitch = up/down movement of the head (positive = up, negative = down)
# Yaw   = left/right rotation of the head (positive = right, negative = left)
# This code assumes a person is making eye contact with the robot if:
# → pitch is between -20° and +20°
# → and yaw is between -20° and +20°
# These values can be adjusted.

# Updated version with automatic logging on eye contact and ctrl+c as stop key

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import math
from Misty_commands import Misty
import base64
from datetime import datetime
import os
import numpy as np
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2

# Create unique log file name
log_file_name = f"log_facepose-{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_file_name)

# Add explanation to top of log file (once at startup)
with open(log_file_path, 'w', encoding='utf-8') as f:
    f.write("LOGGING OF HEAD POSE\n")
    f.write("Each entry includes a timestamp, pitch (up/down), yaw (left/right), and whether eye contact was detected.\n")
    f.write("Pitch = vertical head movement (degrees)\n")
    f.write("Yaw = horizontal head rotation (degrees)\n")
    f.write("Eye contact = YES if pitch AND yaw are both between -20° and +20°\n")
    f.write("-" * 70 + "\n")

# Logging function
def log_facepose(pitch, yaw, eye_contact):
    ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    contact_str = "YES" if eye_contact else "NO"
    with open(log_file_path, 'a', encoding='utf-8') as f:
        f.write(f"{ct}\tPitch: {pitch:.2f}°\tYaw: {yaw:.2f}°\tEye contact: {contact_str}\n")
    print(f"Log saved to {log_file_path}")

def draw_landmarks_on_image(rgb_image, detection_result):
    face_landmarks_list = detection_result.face_landmarks
    annotated_image = np.copy(rgb_image)
    for face_landmarks in face_landmarks_list:
        face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        face_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z)
            for landmark in face_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_tesselation_style())
        solutions.drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_contours_style())
        solutions.drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks_proto,
            connections=mp.solutions.face_mesh.FACEMESH_IRISES,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_iris_connections_style())
    return annotated_image

def FaceLandmarker():
    base_options = python.BaseOptions(model_asset_path='face_landmarker_v2_with_blendshapes.task')
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
        num_faces=1)
    return vision.FaceLandmarker.create_from_options(options)

def getMistyImage(misty):
    result = misty.take_picture(base64=True, fileName="TempImage01", width=800, height=600,
                                displayOnScreen=False, overwriteExisting=True)
    if result.json()['status'] == "Success":
        result = misty.get_image(fileName="TempImage01.jpg", base64=True)
        image = result.json()['result']['base64']
        decoded_data = base64.b64decode(image)
        np_data = np.frombuffer(decoded_data, np.uint8)  # fixed from deprecated fromstring
        img = cv2.imdecode(np_data, cv2.IMREAD_UNCHANGED)
        return True, img
    else:
        return False, None

def DetectHeadPose(cv_image, detector):
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv_image)
    detection_result = detector.detect(image)
    return detection_result, image

def rotation_matrix_to_angles(rotation_matrix):
    x = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
    y = math.atan2(-rotation_matrix[2, 0], math.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2))
    z = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
    return np.array([x, y, z]) * 180. / math.pi

def get_pitch_yaw():
    print("Initializing FaceLandmarker()")
    detector = FaceLandmarker()
    im_name = "Head Pose Estimation Including Pitch And Yaw"
    done = False
    while not done:
        print("Attempting to capture image from Misty...")
        return_value, cv_image = getMistyImage(misty)
        if not return_value:
            print("Failed to capture image from camera.")
            continue

        detection_result, image = DetectHeadPose(cv_image, detector)

        face_coordination_in_real_world = np.array([
            [285, 528, 200], [285, 371, 152], [197, 574, 128],
            [173, 425, 108], [360, 574, 128], [391, 425, 108]
        ], dtype=np.float64)

        h, w = 800, 600
        face_coordination_in_image = []

        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        results = face_mesh.process(cv_image)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for idx, lm in enumerate(face_landmarks.landmark):
                    if idx in [1, 9, 57, 130, 287, 359]:
                        x, y = int(lm.x * w), int(lm.y * h)
                        face_coordination_in_image.append([x, y])

                face_coordination_in_image = np.array(face_coordination_in_image, dtype=np.float64)
                focal_length = 1 * w
                cam_matrix = np.array([[focal_length, 0, w / 2], [0, focal_length, h / 2], [0, 0, 1]])
                dist_matrix = np.zeros((4, 1), dtype=np.float64)

                success, rotation_vec, transition_vec = cv2.solvePnP(
                    face_coordination_in_real_world, face_coordination_in_image, cam_matrix, dist_matrix)
                rotation_matrix, _ = cv2.Rodrigues(rotation_vec)
                pitch, yaw, roll = rotation_matrix_to_angles(rotation_matrix)

                print(f'Pitch: {pitch:.2f}°, Yaw: {yaw:.2f}°')

                # Eye contact detection
                eye_contact = abs(pitch) < 20 and abs(yaw) < 20
                log_facepose(pitch, yaw, eye_contact)

                for i, (k, v) in enumerate(zip(('pitch', 'yaw', 'roll'), (pitch, yaw, roll))):
                    text = f'{k}: {int(v)}'
                    cv2.putText(cv_image, text, (20, i * 30 + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 0, 200), 2)

        annotated_image = draw_landmarks_on_image(cv_image, detection_result)
        cv2.imshow(im_name, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
        key = cv2.waitKey(1)
        if key == ord('q'):  # Press 'q' to stop
            print("Key 'q' pressed. Exiting program.")
            break

    cv2.destroyWindow(im_name)
    return pitch, yaw

if __name__ == "__main__":
    misty = Misty(ip_address="192.168.0.100")
    print("Main was started")
    try:
        get_pitch_yaw()
    except Exception as e:
        print(f"An error occurred: {e}")
