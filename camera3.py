import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
from gpiozero import Buzzer

buzzer = Buzzer(17)

# Load face detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Download from http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2

# Constants for drowsiness detection
EAR_THRESHOLD = 0.30  # Eye Aspect Ratio threshold for detecting blink
CONSECUTIVE_FRAMES_THRESHOLD = 5  # Number of consecutive frames the eyes must be below EAR_THRESHOLD to indicate drowsiness
BLINK_DURATION_THRESHOLD = 0.20  # Minimum duration of a blink in seconds
EYES_NOT_DETECTED_THRESHOLD = 3  # Number of consecutive frames where eyes are not detected to generate an alert

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
face_consecutive_frames = 0
blink_start_time = None
blink_count = 0
eyes_not_detected_frames = 0

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)

    if len(faces) == 0:
        # Increment the frames where face is not detected
        eyes_not_detected_frames += 1
        if eyes_not_detected_frames >= EYES_NOT_DETECTED_THRESHOLD:
            # Face is not detected for a certain period, generate an alert
            print("ALERT! Face not detected. Please face the camera.")
            buzzer.off()
            eyes_not_detected_frames = 0
    else:
        # Reset the frames where face is not detected
        eyes_not_detected_frames = 0
        buzzer.on()

    for face in faces:
        landmarks = predictor(gray, face)

        # Extract face landmarks coordinates
        face_landmarks = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(68)]

        # Draw points and lines for the face
        for i, (x, y) in enumerate(face_landmarks):
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
            cv2.putText(frame, f"{i+1}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        cv2.polylines(frame, [np.array(face_landmarks, dtype=np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)

        # Check for drowsiness based on consecutive frame counts
        face_consecutive_frames = is_blinking(face_landmarks, face_consecutive_frames)

        if face_consecutive_frames >= CONSECUTIVE_FRAMES_THRESHOLD:
            buzzer.on()
            if blink_start_time is None:
                blink_start_time = cv2.getTickCount()
                blink_count += 1
            else:
                elapsed_time = (cv2.getTickCount() - blink_start_time) / cv2.getTickFrequency()
                if elapsed_time >= BLINK_DURATION_THRESHOLD:
                    # Drowsiness detected, you can trigger an alert here
                    print("ALERT! Drowsiness detected.")
                    buzzer.off()
                    blink_start_time = None
        else:
            blink_start_time = None

    # Display the frame
    cv2.imshow("Drowsiness Detection", frame)

    # Break the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
