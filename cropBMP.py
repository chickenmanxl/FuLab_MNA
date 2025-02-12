from PIL import Image
import os

# Directory containing BMP images
input_dir = 'C:\\Users\\cneje\\Downloads\\2024_10_22-24_MNA_Testing'
output_dir = 'C:\\Users\\cneje\\Downloads\\2024_10_22-24_MNA_Testing\\Cropped'

# Desired crop size (left, upper, right, lower)
crop_box = (150, 200, 2592, 1809)

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Iterate over all files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".bmp"):
        # Open image
        img_path = os.path.join(input_dir, filename)
        img = Image.open(img_path)

        # Crop image
        cropped_img = img.crop(crop_box)

        # Save cropped image to the output directory
        cropped_img.save(os.path.join(output_dir, filename))

        print(f"Cropped and saved: {filename}")

print("Cropping completed for all images.")
