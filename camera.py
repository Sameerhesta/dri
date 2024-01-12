import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
from collections import deque
from gpiozero import Buzzer


buzzer = Buzzer(17)

 
# Load face detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Download from http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
 
# Constants for drowsiness detection
EAR_THRESHOLD = 0.30  # Eye Aspect Ratio threshold for detecting blink
CONSECUTIVE_FRAMES_THRESHOLD = 10  # Number of consecutive frames the eyes must be below EAR_THRESHOLD to indicate drowsiness
BLINK_DURATION_THRESHOLD = 0.20  # Minimum duration of a blink in seconds
EYES_NOT_DETECTED_THRESHOLD = 5  # Number of consecutive frames where eyes are not detected to generate an alert
 
# Function to calculate eye aspect ratio (EAR)
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear
 
# Function to detect blink
def is_blinking(eye, consecutive_frames):
    ear = eye_aspect_ratio(eye)
    if ear < EAR_THRESHOLD:
        consecutive_frames += 1
    else:
        consecutive_frames = 0
    return consecutive_frames
 
# Initialize webcam
cap = cv2.VideoCapture(0)
 
# Initialize variables for drowsiness detection
left_consecutive_frames = 0
right_consecutive_frames = 0
blink_start_time = None
blink_count = 0
eyes_not_detected_frames = 0
 
while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 
    faces = detector(gray)

    if len(faces) == 0:
        # Increment the frames where eyes are not detected
        eyes_not_detected_frames += 1
        if eyes_not_detected_frames >= EYES_NOT_DETECTED_THRESHOLD:
            # Eyes are not detected for a certain period, generate an alert
            print("ALERT! Eyes not detected. Please face the camera.")
            buzzer.off()
            eyes_not_detected_frames = 0
    else:
        # Reset the frames where eyes are not detected
        eyes_not_detected_frames = 0
        buzzer.on()
 
    for face in faces:
        landmarks = predictor(gray, face)

         # Extract coordinates of points 1 (left corner of the left eye) and 37 (right corner of the right eye)
        point_1 = (landmarks.part(0).x, landmarks.part(0).y)
        point_40 = (landmarks.part(40).x, landmarks.part(40).y)

        # Calculate the Euclidean distance between points 1 and 37
        distance_1_40 = dist.euclidean(point_1, point_40)

        # Display the distance on the frame
        cv2.putText(frame, f"Face position: {distance_1_40:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        if(distance_1_40 <20 or distance_1_40 > 105):
            print("ALERT! Eyes not detected. Please face the camera.")
            # cv2.putText(frame, f"ALERT! Eyes not detected. Please face the camera.", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            buzzer.off()
            eyes_not_detected_frames = 0
        else:
            buzzer.on()
            

        # Extract left and right eye coordinates
        left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
        right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]
 
        # Detect blinks and update consecutive frame counts
        left_consecutive_frames = is_blinking(left_eye, left_consecutive_frames)
        right_consecutive_frames = is_blinking(right_eye, right_consecutive_frames)
 
        # Check for drowsiness based on consecutive frame counts
        if left_consecutive_frames >= CONSECUTIVE_FRAMES_THRESHOLD or right_consecutive_frames >= CONSECUTIVE_FRAMES_THRESHOLD:
            buzzer.on()
            if blink_start_time is None:
                blink_start_time = cv2.getTickCount()
                blink_count += 1
            else:
                elapsed_time = (cv2.getTickCount() - blink_start_time) / cv2.getTickFrequency()
                if elapsed_time >= BLINK_DURATION_THRESHOLD:
                    # Drowsiness detected, you can trigger an alert here
                    print("ALERT! Drowsiness detected.")
                    # cv2.putText(frame, f"Drowsiness detected: {(100 - left_ear*100) :.2f}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    buzzer.off()
                    blink_start_time = None
        else:
            blink_start_time = None
 
        # Calculate and display the eye aspect ratio
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
 
        # Draw landmarks on the frame
        # for eye in [left_eye, right_eye]:
        #     for (x, y) in eye:
        #         cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
 
        # Display numerical representation of drowsiness
        cv2.putText(frame, f"Left EAR: {left_ear:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f"Right EAR: {right_ear:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        # cv2.putText(frame, f"Total Drowsiness: {blink_count/2}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
 
    # Display the frame
    cv2.imshow("Camera with Face Recognition for Distraction and Drowsiness Detection", frame)
 
    # Break the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
 
# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()