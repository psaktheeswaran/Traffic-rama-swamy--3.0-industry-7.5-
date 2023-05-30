import cv2
import numpy as np
import datetime
import csv
import os

# Load YOLO model and coco.names
net = cv2.dnn.readNet('yolov3-tiny.weights', 'yolov3-tiny.cfg')
with open('co.names', 'r') as f:
    classes = f.read().splitlines()

# Load custom transparent PNG image to overlay
stitch_image = cv2.imread('fff.png', cv2.IMREAD_UNCHANGED)

# Initialize video capture
cap = cv2.VideoCapture('catt.mp4')  # Use 0 for webcam, or provide the video file path

# Set default window size
window_width = 800
window_height = 600

# Create resizable window
cv2.namedWindow('Face Stitching', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Face Stitching', window_width, window_height)

# Create output folder if it doesn't exist
output_folder = 'output'
os.makedirs(output_folder, exist_ok=True)

# Open CSV file for writing detection data
csv_file = open('detection.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Timestamp', 'Class'])

while True:
    # Read frame from video capture
    ret, frame = cap.read()
    if not ret:
        break

    # Resize frame to match window size
    frame = cv2.resize(frame, (window_width, window_height))

    # Perform object detection using YOLO
    blob = cv2.dnn.blobFromImage(frame, 1/255, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    output_layers_names = net.getUnconnectedOutLayersNames()
    layer_outputs = net.forward(output_layers_names)

    # Process detected objects using Non-Maximum Suppression
    person_boxes = []
    confidences = []
    class_ids = []

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5 and class_id == 0:  # 0 represents the 'person' class
                center_x = int(detection[0] * frame.shape[1])
                center_y = int(detection[1] * frame.shape[0])
                w = int(detection[2] * frame.shape[1])
                h = int(detection[3] * frame.shape[0])

                # Calculate bounding box coordinates
                x = int(center_x - w/2)
                y = int(center_y - h/2)

                person_boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indices = cv2.dnn.NMSBoxes(person_boxes, confidences, 0.5, 0.4)

    for i in indices:
        i = i
        x, y, w, h = person_boxes[i]
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, classes[class_ids[i]], (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        csv_writer.writerow([datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), classes[class_ids[i]]])

        # Crop the face region from the frame
        face_roi = frame[y:y+h, x:x+w]

        # Resize the stitch image to match the size of the face region
        stitch_image_resized = cv2.resize(stitch_image, (w, h))

        # Create an alpha channel for the overlay image
        alpha = np.expand_dims(stitch_image_resized[:, :, 3] / 255.0, axis=2)

        # Overlay the stitch image onto the face region
        overlay = (1 - alpha) * face_roi + alpha * stitch_image_resized[:, :, :3]
        overlay = overlay.astype(np.uint8)

        # Replace the face region with the overlay
        frame[y:y+h, x:x+w] = overlay

    # Display the frame in the window
    cv2.imshow('Face Stitching', frame)

    # Check for 'q' key press to exit
    if cv2.waitKey(1) == ord('q'):
        break

# Release video capture and close windows
cap.release()
csv_file.close()
cv2.destroyAllWindows()

