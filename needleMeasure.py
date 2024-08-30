# This program seperates data by array and needle, labeling the measurements taken
import pandas as pd

# Load the CSV file
files = ['freddy_results','freddy_coated_results','leilani_coated_results','leilani_results']
for i in files:    
    file_path = f"D:\Fu_Lab\\SESEY\\{i}.csv"
    data = pd.read_csv(file_path, header=None)

    # Extract base widths (Length values from odd rows) and heights (Length values from even rows)
    base_widths = data.iloc[2::2, 3].reset_index(drop=True)
    heights = data.iloc[1::2, 3].reset_index(drop=True)

    # Create a new DataFrame for the labeled data
    labeled_data_corrected = pd.DataFrame({
        'Needle': range(1, len(base_widths) + 1),
        'Array': (base_widths.index // 3) + 1,
        'Height (microns)': heights,
        'Base Width (microns)': base_widths
    })

    # Save the labeled DataFrame to a new Excel file
    output_file_path = f"D:\Fu_Lab\SESEY\labeled_{i}.xlsx"
    labeled_data_corrected.to_excel(output_file_path, index=False)

    print(f"Labeled data has been saved to {output_file_path}")
