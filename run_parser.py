import os
import tkinter as tk
from tkinter import filedialog
import pandas as pd
from broker_data_parser import transform_data

def select_file():
    """Open a file dialog to select a CSV file."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    file_path = filedialog.askopenfilename(
        title="Select CSV file",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    return file_path

def main():
    print("Broker Data Parser")
    print("=" * 50)
    
    # Select input file
    input_file = select_file()
    if not input_file:
        print("No file selected. Exiting...")
        return
    
    print(f"\nSelected file: {input_file}")
    
    # Create output file name
    file_name = os.path.basename(input_file)
    file_name_without_ext = os.path.splitext(file_name)[0]
    output_file = f"{file_name_without_ext}_parsed.xlsx"
    
    try:
        # Process the file
        print("\nProcessing file...")
        transform_data(input_file, output_file)
        
        # Display results
        print(f"\nResults saved to: {output_file}")
        result_df = pd.read_excel(output_file)
        
        print("\nParsed Data Summary:")
        print("=" * 80)
        print(f"Total operations processed: {len(result_df)}")
        print("\nOperation Types:")
        print(result_df['operation_type'].value_counts())
        print("\nSample of parsed data:")
        print(result_df.head())
        
    except Exception as e:
        print(f"\nError processing file: {str(e)}")
        return

if __name__ == "__main__":
    main() 