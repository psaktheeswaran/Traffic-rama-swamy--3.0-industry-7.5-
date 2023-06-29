import cv2
import numpy as np
import pyrebase
import mysql.connector
import csv
from datetime import datetime

# Firebase configuration
firebase_config = {
    "apiKey": "<FIREBASE_API_KEY>",
    "authDomain": "<FIREBASE_AUTH_DOMAIN>",
    "databaseURL": "<FIREBASE_DATABASE_URL>",
    "storageBucket": "<FIREBASE_STORAGE_BUCKET>"
}

# MySQL database configuration
mysql_config = {
    "host": "<MYSQL_HOST>",
    "database": "<MYSQL_DATABASE>",
    "user": "<MYSQL_USER>",
    "password": "<MYSQL_PASSWORD>"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
storage = firebase.storage()

# Initialize MySQL connection
mysql_connection = mysql.connector.connect(**mysql_config)
mysql_cursor = mysql_connection.cursor()

# Load YOLO weights and configuration
net = cv2.dnn.readNet("yolo-tiny.weights", "yolo-tiny.cfg")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

# Load COCO class labels
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Generate random colors for class labels
colors = np.random.uniform(0, 255, size=(len(classes), 3))

# Define the output layer names
layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# Initialize webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width, _ = frame.shape

    # Preprocess frame for YOLO input
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Initialize lists for bounding boxes, confidences, and class IDs
    boxes = []
    confidences = []
    class_ids = []

    # Parse YOLO outputs
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Calculate bounding box coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                # Store bounding box, confidence, and class ID
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply non-maximum suppression to eliminate redundant overlapping boxes
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Process the detected objects
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = classes[class_ids[i]]
            confidence = confidences[i]

            # Crop the detected object
            cropped_img = frame[y:y + h, x:x + w]

            # Generate a timestamp for the detection
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Save the cropped image to Firebase storage
            image_name = f"detection_{timestamp}.jpg"
            cv2.imwrite(image_name, cropped_img)
            storage.child(image_name).put(image_name)

            # Log the detection in CSV
            with open("detection_log.csv", "a") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([timestamp, label, confidence])

            # Save the detection in MySQL database
            sql = "INSERT INTO detections (timestamp, label, confidence) VALUES (%s, %s, %s)"
            values = (timestamp, label, confidence)
            mysql_cursor.execute(sql, values)
            mysql_connection.commit()

            # Save the detection with a timestamp on Firebase
            firebase_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            detection_data = {
                "timestamp": firebase_timestamp,
                "label": label,
                "confidence": confidence
            }
            storage.child(f"detection_{timestamp}.json").put(detection_data)

            # Draw bounding box and label on the frame
            color = colors[class_ids[i]]
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f"{label}: {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Display the frame with bounding boxes and labels
    cv2.imshow("YOLO Object Detection", frame)
    if cv2.waitKey(1) == ord("q"):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
mysql_connection.close()

