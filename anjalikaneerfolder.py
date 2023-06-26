import cv2
import os

# Step 2: Import the required libraries

# Step 3: Set the paths for the input and output folders
input_folder = "CatDetection"
output_folder = "StitchedImages"

# Step 4: Load the given image (df.jpg) to stitch the cropped images onto it
given_image = cv2.imread("df.jpg")

# Step 5: Iterate over the cropped cat images in the input folder
for file_name in os.listdir(input_folder):
    if file_name.endswith(".jpg"):
        # Step 6: Load the cat image
        cat_image = cv2.imread(os.path.join(input_folder, file_name))
        
        # Step 7: Resize the cat image to match the desired size for stitching
        cat_image = cv2.resize(cat_image, (100, 100))
        
        # Step 8: Determine the position where the cat image will be placed on the given image
        position_x = 50  # Set the desired x-coordinate
        position_y = 50  # Set the desired y-coordinate
        
        # Step 9: Overlay the cat image onto the given image
        given_image[position_y:position_y + cat_image.shape[0], position_x:position_x + cat_image.shape[1]] = cat_image
        
        # Step 9: Save the stitched image to the output folder
        output_path = os.path.join(output_folder, "stitched_" + file_name)
        cv2.imwrite(output_path, given_image)
        
        # Step 10: Display the stitched image
        cv2.imshow("Stitched Image", given_image)
        cv2.waitKey(0)

# Step 11: Cleanup and close any open windows
cv2.destroyAllWindows()

