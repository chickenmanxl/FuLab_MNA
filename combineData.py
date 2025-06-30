import os
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_excel_files(folder_path, output_path):
    # Dictionary to hold data for different sheets
    data_dict = {}

    # Iterate over each file in the folder
    for file_name in os.listdir(folder_path):
        print(file_name)
        if file_name.endswith(".xlsx"):
            file_path = os.path.join(folder_path, file_name)
            
            # Extract details from the file name (assuming format is X_X_X_X.xlsx)
            file_parts = file_name.split('_')
            if len(file_parts) < 3:
                logging.warning(f"Skipping file {file_name} due to unexpected filename format.")
                continue
            
            num_needles = file_parts[0]
            test_type = file_parts[3]  # "c" or "i"
            
            # Create a sheet name based on test type and needle count
            sheet_name = f"{num_needles}_needle_{test_type}"

            try:
                # Read the Excel file
                df = pd.read_excel(file_path)
            except Exception as e:
                logging.error(f"Failed to read file {file_name}: {str(e)}")
                continue
            
            # Check if "Displacement (mm)" column exists
            displacement_column = 'Displacement (mm)'
            if displacement_column not in df.columns:
                logging.warning(f"'{displacement_column}' column not found in {file_name}. Skipping file.")
                continue

            # Round displacement values to 2 decimal places
            df[displacement_column] = df[displacement_column].round(2)

            # Select only "Force (N)" and "Displacement (mm)" columns
            df_subset = df[[displacement_column, 'Force (N)']]

            # Rename "Force (N)" column uniquely based on the file name to avoid conflicts
            df_subset = df_subset.rename(columns={'Force (N)': f'Force (N)_{file_name}'})

            # If the sheet_name doesn't exist in the dictionary, initialize it with the first dataset
            if sheet_name not in data_dict:
                logging.info(f'Adding sheet {sheet_name}')
                data_dict[sheet_name] = df_subset
            else:
                # Merge on "Displacement (mm)" to keep a single displacement column and add force columns
                logging.info('Merging data')
                data_dict[sheet_name] = pd.merge(data_dict[sheet_name], 
                                                 df_subset, 
                                                 how='outer', 
                                                 on=displacement_column)

    # Write to the output Excel file with separate sheets
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet_name, data in data_dict.items():
                data.to_excel(writer, sheet_name=sheet_name, index=False)
    except Exception as e:
        logging.error(f"Failed to write to output file: {str(e)}")
        return

    logging.info('Done!')

# Folder containing your Excel files
folder_path = 'C:\\Users\\cneje\\Downloads\\2025_02_ClearCureTesting'

# Output file path
output_file = 'C:\\Users\\cneje\\Downloads\\2025_02_ClearCureTesting\\combined_data.xlsx'

# Run the function to process files and create the output
process_excel_files(folder_path, output_file)