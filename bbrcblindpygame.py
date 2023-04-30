import cv2
import numpy as np
import pygame

# Load the YOLO model
net = cv2.dnn.readNet("face-yolov3-tiny_41000 .weights", "face-yolov3-tiny.cfg")
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Set up the video capture device
cap = cv2.VideoCapture(0)

# Initialize Pygame mixer
pygame.mixer.init()

while True:
    # Capture a frame from the camera
    ret, frame = cap.read()

    # Convert the image to a blob
    height, width, _ = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 1/255, (416, 416), swapRB=True)

    # Pass the blob through the network
    net.setInput(blob)
    output_layers = net.getUnconnectedOutLayersNames()
    layer_outputs = net.forward(output_layers)

    # Process the output
    boxes = []
    confidences = []
    class_ids = []
    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w/2)
                y = int(center_y - h/2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply non-max suppression to eliminate redundant overlapping boxes
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Draw the boxes and class labels
    font = cv2.FONT_HERSHEY_PLAIN
    colors = np.random.uniform(0, 255, size=(len(boxes), 3))
    if len(indexes) > 0:
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = str(round(confidences[i], 2))
            color = colors[i]
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, label + " " + confidence, (x, y-5), font, 1, color, 2)

            # Draw a line between the object and the center of the frame
            cv2.line(frame, (x+w//2, y+h//2), (width//2, height//2), (0, 255, 0), 2)

            # Check the distance between the object and the center of the frame
            distance = np.sqrt((x+w//2 - width//2)**2 + (y+h//2 - height//2)**2)
            if distance < 1000:
                # Load and play an MP3 file for the detected class
                if label == "person":
                    sound_file = "person.mp3"
                elif label == "car":
                    sound_file = "car.mp3"
                else:
                    sound_file = "default.mp3"

                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    continue

    # Display the resulting image
    cv2.imshow("Object Detection", frame)

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) == ord('q'):
        break

# Release the video capture device and close all windows
cap.release()
cv2.destroyAllWindows()

   

