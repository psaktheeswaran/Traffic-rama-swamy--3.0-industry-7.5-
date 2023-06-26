import cv2
import numpy as np

# Step 1: Install the required libraries
# pip install opencv-python
# pip install numpy

# Step 2: Download the necessary files: yolov3-tiny.weights, yolov3-tiny.cfg, and coco.names

# Step 3: Import the required libraries

# Step 4: Load the YOLOv3-tiny model and the COCO class labels
net = cv2.dnn.readNet('yolov3-tiny.weights', 'yolov3-tiny.cfg')
classes = []
with open('coco.names', 'r') as f:
    classes = [line.strip() for line in f.readlines()]

# Step 5: Set up the webcam and start capturing frames
cap = cv2.VideoCapture(0)

# Step 6: Preprocess the frame for the model
while True:
    ret, frame = cap.read()

    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layers_names = net.getLayerNames()
    output_layers = [layers_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    # Step 7: Forward pass through the network and get the detections
    outputs = net.forward(output_layers)
    class_ids = []
    confidences = []
    boxes = []
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5 and class_id == 0:  # Checking if it's a person (class_id 0)
                # Object detected as a person
                # ...
                continue  # Skip cropping process if person is detected

            if confidence > 0.5 and class_id == 17:  # Checking if it's a cat (class_id 17)
                # Object detected as a cat
                center_x = int(detection[0] * frame.shape[1])
                center_y = int(detection[1] * frame.shape[0])
                width = int(detection[2] * frame.shape[1])
                height = int(detection[3] * frame.shape[0])
                x = int(center_x - width / 2)
                y = int(center_y - height / 2)

                cropped_cat = frame[y:y+height, x:x+width]
                # Save cropped cat image with high quality
                cv2.imwrite(f'cropped_cat_{str(i).zfill(6)}.jpg', cropped_cat, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                i += 1
                if i > 1000000:
                    break

    # Step 9: Display the frame with bounding boxes and labels
    color = (255, 0, 0)  # Blue color for cat bounding box
    cv2.rectangle(frame, (x, y), (x + width, y + height), color, 2)
    cv2.putText(frame, classes[class_id], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Step 10: Show the resulting frame
    cv2.imshow('Cat Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

