import cv2
import dlib
from scipy.spatial import distance as dist
from gpiozero import Buzzer

buzzer = Buzzer(17)

# Load face detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Constants for drowsiness detection
EAR_THRESHOLD = 0.30
CONSECUTIVE_FRAMES_THRESHOLD = 5
BLINK_DURATION_THRESHOLD = 0.20
EYES_NOT_DETECTED_THRESHOLD = 3
left_consecutive_frames = 0
right_consecutive_frames = 0


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

            # Extract left and right eye coordinates
            left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
            right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]

            # Calculate and display the eye aspect ratio
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)

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
                        buzzer.off()
                        blink_start_time = None
            else:
                blink_start_time = None

            # Draw lines indicating the face
            for i in range(0, 68):
                cv2.line(frame, (landmarks.part(i).x, landmarks.part(i).y),
                         (landmarks.part((i + 1) % 68).x, landmarks.part((i + 1) % 68).y), (0, 255, 0), 1)

            # Display numerical representation of drowsiness
            cv2.putText(frame, f"Left EAR: {left_ear:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"Right EAR: {right_ear:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"Blink Count: {blink_count}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Display the frame
    cv2.imshow("Drowsiness Detection", frame)

    # Break the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
