import os
from PIL import Image

def stitch_images(image_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Dictionary to hold lists of images by the second and third parts of the filename
    images_by_group = {}

    # Iterate through all images in the directory
    for filename in os.listdir(image_dir):
        #if filename.startswith("10_") and filename.endswith(".bmp"):  # Filter by the first number "10"
            parts = filename.split('_')
            if len(parts) >= 3:  # Ensure the filename has at least three parts
                group_key = f"{parts[0]}_{parts[1]}_{parts[2]}"  # Use the second and third numbers as the key
                if group_key not in images_by_group:
                    images_by_group[group_key] = []
                images_by_group[group_key].append(filename)

    # Stitch images together by group
    for group_key, files in images_by_group.items():
        # Sort files to ensure correct order
        files.sort()

        # Open all images
        images = [Image.open(os.path.join(image_dir, f)) for f in files]

        # Calculate total width and max height for the output image
        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)

        # Create a new blank image with the total width and max height
        new_image = Image.new('RGB', (total_width, max_height))

        # Paste each image side by side
        x_offset = 0
        for img in images:
            new_image.paste(img, (x_offset, 0))
            x_offset += img.width

        # Save the combined image
        output_filename = f"{group_key}_combined.bmp"
        output_path = os.path.join(output_dir, output_filename)
        new_image.save(output_path)
        print(f"Saved combined image: {output_path}")

# Example usage:
image_dir = 'C:/Users/cneje/Downloads/2024_08_27_MNA_Images_cropped'  # Directory containing your cropped images
output_dir = 'C:/Users/cneje/Downloads/2024_08_27_MNA_Images_combined'  # Directory to save the combined images
stitch_images(image_dir, output_dir)
