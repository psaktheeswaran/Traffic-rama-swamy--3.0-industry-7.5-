import cv2
import numpy as np
import playsound

# Load the YOLOv3-tiny network
net = cv2.dnn.readNet("yolov3-tiny.weights", "yolov3-tiny.cfg")

# Load the COCO class names
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Initialize the video stream and set the frame size
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Set the minimum distance for playing the sound
min_distance = 50

while True:
    # Read a frame from the video stream
    ret, frame = cap.read()

    # Convert the frame to a blob
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)

    # Pass the blob through the network and get the detections
    net.setInput(blob)
    outs = net.forward(getOutputsNames(net))

    # Initialize the lists for the detected class IDs, confidences, and bounding boxes
    class_ids = []
    confidences = []
    boxes = []

    # Process the detections
    for out in outs:
        for detection in out:
            # Get the class ID and confidence
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            # Filter out weak detections
            if confidence > 0.5:
                # Get the center coordinates and dimensions of the bounding box
                cx = int(detection[0] * frame.shape[1])
                cy = int(detection[1] * frame.shape[0])
                w = int(detection[2] * frame.shape[1])
                h = int(detection[3] * frame.shape[0])

                # Calculate the top-left and bottom-right coordinates of the bounding box
                x = cx - w // 2
                y = cy - h // 2
                x2 = x + w
                y2 = y + h

                # Add the class ID, confidence, and bounding box coordinates to the lists
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])

    # Apply non-maximum suppression to remove overlapping detections
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Draw the bounding boxes and class labels for the remaining detections
    for i in indices:
        i = i
        box = boxes[i]
        x, y, w, h = box

        # Draw the bounding box
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Draw a line from the center of the bounding box to the center of the frame
        cx = x + w // 2
        cy = y + h // 2
        cv2.line(frame, (cx, cy), (frame.shape[1] // 2, frame.shape[0] // 2), (0, 0, 255), 2)

                # Play a sound if the object is too close
        if getDistance(cx, cy, frame.shape[1] // 2, frame.shape[0] // 2) < min_distance:
            class_name = classes[class_ids[i]]

            # Play the sound corresponding to the class name
            if class_name == "person":
                playsound.playsound("person.mp3")
            elif class_name == "car":
                playsound.playsound("car.mp3")
            elif class_name == "dog":
                playsound.playsound("dog.mp3")

    # Show the frame
    cv2.imshow("Object Detection", frame)

    # Break the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video stream and close all windows
cap.release()
cv2.destroyAllWindows()


