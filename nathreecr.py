import cv2
import numpy as np
import datetime
import csv
import os

# Load YOLO model and coco.names
net = cv2.dnn.readNet('yolov3-tiny.weights', 'yolov3-tiny.cfg')
with open('co.names', 'r') as f:
    classes = f.read().splitlines()

# Load custom transparent PNG image to stitch on the person
person_stitch_image = cv2.imread('fff.png', cv2.IMREAD_UNCHANGED)

# Load custom transparent PNG image to overlay on the chair
chair_overlay_image = cv2.imread('nnn.png', cv2.IMREAD_UNCHANGED)

# Initialize video capture
cap = cv2.VideoCapture('catt.mp4')  # Use 0 for webcam, or provide the video file path

# Set default window size
window_width = 800
window_height = 600

# Create resizable window
cv2.namedWindow('Object Detection', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Object Detection', window_width, window_height)

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
    chair_boxes = []
    confidences = []
    class_ids = []

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                center_x = int(detection[0] * frame.shape[1])
                center_y = int(detection[1] * frame.shape[0])
                w = int(detection[2] * frame.shape[1])
                h = int(detection[3] * frame.shape[0])

                # Calculate bounding box coordinates
                x = int(center_x - w/2)
                y = int(center_y - h/2)

                if class_id == 0:  # 0 represents the 'person' class
                    person_boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
                elif class_id == 63:  # 63 represents the 'chair' class
                    chair_boxes.append([x, y, w, h])

    # Check if a person and chair are detected at the same time
    person_detected = len(person_boxes) > 0
    chair_detected = len(chair_boxes) > 0
    if person_detected and chair_detected:
        person_box = person_boxes[0]  # Assuming only one person and one chair are detected
        chair_box = chair_boxes[0]
    elif person_detected:
        person_box = person_boxes[0]
        chair_box = None
    else:
        person_box = None
        chair_box = None

    # Save detection data to CSV file
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if person_detected or chair_detected:
        if person_detected and chair_detected:
            csv_writer.writerow([timestamp, 'Person and Chair'])
        elif person_detected:
            csv_writer.writerow([timestamp, 'Person'])
        else:
            csv_writer.writerow([timestamp, 'Chair'])

    # Crop and save the person image if detected
    if person_box is not None:
        x, y, w, h = person_box
        person_image = frame[y:y+h, x:x+w]
        person_output_path = os.path.join(output_folder, f'person_{timestamp}.jpg')
        cv2.imwrite(person_output_path, person_image)

    # Apply non-maximum suppression to the detected boxes
    indices = cv2.dnn.NMSBoxes(person_boxes + chair_boxes, confidences, 0.5, 0.4)

    # Apply stitching on the person and overlay chair image
    for i in indices:
        i = i
        if i < len(person_boxes):
            if person_box is not None:
                x, y, w, h = person_box
                # Resize the stitch image to match the person region
                stitch_resized = cv2.resize(person_stitch_image, (w, h))

                # Extract the alpha channel from the stitch image
                stitch_alpha = stitch_resized[:, :, 3] / 255.0

                # Create a mask from the alpha channel
                mask = np.stack([stitch_alpha] * 3, axis=2)

                # Invert the mask
                inv_mask = 1 - mask

                # Adjust the stitch image size if it does not match the person region
                if stitch_resized.shape[0] != h or stitch_resized.shape[1] != w:
                    stitch_resized = cv2.resize(stitch_resized, (w, h))

                # Resize the frame region to match the stitch image
                person_region_resized = cv2.resize(frame[y:y+h, x:x+w], (w, h))

                # Apply the stitch image on the person region using the mask
                stitched_face = cv2.multiply(person_region_resized.astype(np.float32), inv_mask, dtype=cv2.CV_32F)
                stitched_image = cv2.multiply(stitch_resized[:, :, :3].astype(np.float32), mask, dtype=cv2.CV_32F)
                stitch_applied = cv2.add(stitched_face, stitched_image).astype(np.uint8)

                # Replace the person region in the original frame with the stitched region
                frame[y:y+h, x:x+w] = stitch_applied
        else:
            if chair_box is not None:
                x, y, w, h = chair_box
                # Overlay the chair image on the chair region
                chair_resized = cv2.resize(chair_overlay_image, (w, h))

                # Extract the alpha channel from the chair image
                chair_alpha = chair_resized[:, :, 3] / 255.0

                # Create a mask from the alpha channel
                mask = np.stack([chair_alpha] * 3, axis=2)

                # Invert the mask
                inv_mask = 1 - mask

                # Adjust the chair image size if it does not match the chair region
                if chair_resized.shape[0] != h or chair_resized.shape[1] != w:
                    chair_resized = cv2.resize(chair_resized, (w, h))

                # Resize the frame region to match the chair image
                chair_region_resized = cv2.resize(frame[y:y+h, x:x+w], (w, h))

                # Apply the chair image on the chair region using the mask
                chair_applied = cv2.add(cv2.multiply(chair_region_resized.astype(np.float32), inv_mask, dtype=cv2.CV_32F),
                                        cv2.multiply(chair_resized[:, :, :3].astype(np.float32), mask, dtype=cv2.CV_32F))

                # Replace the chair region in the original frame with the overlaid chair image
                frame[y:y+h, x:x+w] = chair_applied

    # Display the resulting frame
    cv2.imshow('Object Detection', frame)

    # Check for 'q' key to exit
    if cv2.waitKey(1) == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
csv_file.close()

