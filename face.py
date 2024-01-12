import cv2
import face_recognition

# Load known face images and their corresponding names
known_faces = {
    "Sameer": face_recognition.load_image_file("images/Sameer.jpeg"),
    "Aman": face_recognition.load_image_file("images/Amank.jpeg"),
    # Add more faces as needed
}

# Extract face encodings for known faces
known_face_encodings = {name: face_recognition.face_encodings(img)[0] for name, img in known_faces.items()}

# Initialize webcam
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    # Find face locations and face encodings in the current frame
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    # Loop through each face in the current frame
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Check if the face matches any of the known faces
        matches = face_recognition.compare_faces(list(known_face_encodings.values()), face_encoding)

        name = "Unknown"
        if True in matches:
            first_match_index = matches.index(True)
            name = list(known_face_encodings.keys())[first_match_index]

        # Draw a rectangle around the face and display the name
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    # Display the frame
    cv2.imshow("Face Recognition", frame)

    # Break the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()


# Extract face encodings for known faces
known_face_encodings = {name: face_recognition.face_encodings(img)[0] for name, img in known_faces.items()}

# Initialize webcam
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    # Find face locations and face encodings in the current frame
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    # Loop through each face in the current frame
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Check if the face matches any of the known faces
        matches = face_recognition.compare_faces(list(known_face_encodings.values()), face_encoding)

        name = "Unknown"
        if True in matches:
            first_match_index = matches.index(True)
            name = list(known_face_encodings.keys())[first_match_index]

        # Draw a rectangle around the face and display the name
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    # Display the frame
    cv2.imshow("Face Recognition", frame)

    # Break the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
