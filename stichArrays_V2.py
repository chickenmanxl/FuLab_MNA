import os
from PIL import Image

def normalize_and_renumber_arrays(image_dir):
    """
    Normalize filenames to collapse multiple underscores, group files by array (e.g., `_5_` and `_5a_`),
    and renumber them sequentially within each group.
    """
    files_by_group = {}

    # Normalize filenames to remove double underscores and collect files by group
    for filename in os.listdir(image_dir):
        if filename.endswith(".bmp"):
            normalized_filename = filename.replace('__', '_')  # Remove double underscores
            if normalized_filename != filename:
                # Rename the file to its normalized name
                original_path = os.path.join(image_dir, filename)
                normalized_path = os.path.join(image_dir, normalized_filename)
                os.rename(original_path, normalized_path)
                print(f"Normalized: {filename} -> {normalized_filename}")

            # Split the normalized filename
            parts = normalized_filename.split('_')
            if len(parts) >= 4:  # Ensure the filename has at least four parts
                try:
                    prefix = f"{parts[0]}_{parts[1]}"  # Combine the first two parts as a unique prefix
                    array_key = parts[2]  # The third part is the array identifier (e.g., `_5_`, `_5a_`)
                    needle_number = int(parts[3].split('.')[0])  # Extract the needle number (n)
                    group_key = f"{prefix}_{array_key}"  # Unique key combining prefix and array
                    if group_key not in files_by_group:
                        files_by_group[group_key] = []
                    files_by_group[group_key].append((needle_number, normalized_filename))
                except ValueError:
                    print(f"Skipping file with invalid needle number: {normalized_filename}")

    # Renumber files within each group
    for group_key, files in files_by_group.items():
        # Sort files by needle number within the group
        files.sort(key=lambda x: x[0])

        # First pass: Rename to temporary filenames to avoid conflicts
        for idx, (original_number, filename) in enumerate(files, start=1):
            temp_filename = f"temp_{group_key}_{idx}.bmp"  # Temporary name unique to each group
            original_path = os.path.join(image_dir, filename)
            temp_path = os.path.join(image_dir, temp_filename)
            os.rename(original_path, temp_path)

        # Second pass: Rename to final normalized filenames
        for idx, (original_number, filename) in enumerate(files, start=1):
            parts = filename.split('_')
            parts[3] = f"{idx}.bmp"  # Update the needle number to be sequential
            normalized_filename = '_'.join(parts)
            temp_path = os.path.join(image_dir, f"temp_{group_key}_{idx}.bmp")
            final_path = os.path.join(image_dir, normalized_filename)
            os.rename(temp_path, final_path)
            print(f"Renamed: {filename} -> {normalized_filename}")

    # Renumber files within each group
    for group_key, files in files_by_group.items():
        # Sort files by prefix and needle number within the group
        files.sort(key=lambda x: (int(group_key.split('_')[0]), int(group_key.split('_')[1]), x[0]))

        # First pass: Rename to temporary filenames to avoid conflicts
        for idx, (original_number, filename) in enumerate(files, start=1):
            temp_filename = f"temp_{group_key}_{idx}.bmp"  # Temporary name unique to each group
            original_path = os.path.join(image_dir, filename)
            temp_path = os.path.join(image_dir, temp_filename)
            os.rename(original_path, temp_path)

        # Second pass: Rename to final normalized filenames
        for idx, (original_number, filename) in enumerate(files, start=1):
            parts = filename.split('_')
            parts[3] = f"{idx}.bmp"  # Update the needle number to be sequential
            normalized_filename = '_'.join(parts)
            temp_path = os.path.join(image_dir, f"temp_{group_key}_{idx}.bmp")
            final_path = os.path.join(image_dir, normalized_filename)
            os.rename(temp_path, final_path)
            print(f"Renamed: {filename} -> {normalized_filename}")

def stitch_images(image_dir, output_dir, images_per_array=10):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Dictionary to hold lists of images by group (arrays of images_per_array images)
    images_by_group = {}

    # Iterate through all images in the directory
    for filename in os.listdir(image_dir):
        if filename.endswith(".bmp"):  # Ensure we are processing .bmp files
            parts = filename.split('_')
            if len(parts) >= 4:  # Ensure the filename has at least four parts
                if int(parts[0]) != 1:
                    try:
                        needle_number = int(parts[3].split('.')[0])  # Extract the needle number (n)
                        # Identify which array the needle belongs to
                        array_number = (needle_number - 1) // images_per_array
                        group_key = '_'.join(parts[:3]) + f"_{array_number}"
                        if group_key not in images_by_group:
                            images_by_group[group_key] = []
                        images_by_group[group_key].append((needle_number, filename))
                    except ValueError:
                        print(f"Skipping file with invalid needle number: {filename}")

    # Stitch images together by group
    new_key = 0
    for group_key, files in images_by_group.items():
        # Sort files to ensure correct order within the group
        files.sort(key=lambda x: x[0])  # Sort by needle number

        # Open all images
        images = [Image.open(os.path.join(image_dir, f[1])).rotate(-90, expand=True) for f in files]

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
        new_key += 1

# Define your input and output directories
image_dir = 'C:\\Users\\cneje\\Downloads\\2024_12_3_PigSkin_and_PF_Hand_Insertion'  # Directory containing your cropped images
output_dir = 'C:\\Users\\cneje\\Downloads\\2024_12_3_PigSkin_and_PF_Hand_Insertion\\combined'  # Directory to save the combined images

#normalize_and_renumber_files(image_dir)
stitch_images(image_dir, output_dir)
