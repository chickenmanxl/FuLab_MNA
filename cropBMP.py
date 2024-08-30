from PIL import Image
import os

# Directory containing BMP images
input_dir = 'C:/Users/cneje/Downloads/2024_08_27_MNA_Images'
output_dir = 'C:/Users/cneje/Downloads/2024_08_27_MNA_Images_cropped'

# Desired crop size (left, upper, right, lower)
crop_box = (465, 0, 915, 960)

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
