import csv
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import os

def process_row(row):
    # Skip empty rows and comment lines
    if not row or not row[0].strip() or row[0].startswith(('//', '#', ';')):
        return None

    # Skip header row
    if row[0] == '<ID|readonly|noverify>':
        return None

    if len(row) < 2:
        return None

    identifier = row[0].strip()
    unit_name = row[1].strip()

    # Only process specific suffixes
    if not identifier.endswith(('_0', '_1', '_2', '_shop')):
        return None

    return identifier, unit_name

def process_single_file(file_path):
    #Overwrites the original files
    input_path = Path(file_path)
    temp_output_path = input_path.with_suffix('.tmp')
    
    unit_names = {}
    found_any_valid_rows = False

    # Collect _1 unit names
    with open(input_path, 'r', encoding='utf-8', newline='') as infile:
        reader = csv.reader(infile, delimiter=';')
        next(reader, None) # Skip header

        for row in reader:
            processed = process_row(row)
            if not processed:
                continue

            identifier, unit_name = processed
            found_any_valid_rows = True
            
            if identifier.endswith('_1'):
                base_id = identifier[:-2]
                unit_names[base_id] = unit_name

    if not found_any_valid_rows:
        print(f"Skipping {input_path.name}: No valid unit IDs found to parse.")
        return

    # Write to file (temp)
    with open(temp_output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerow(['<ID|readonly|noverify>', '<English>']) #

        with open(input_path, 'r', encoding='utf-8', newline='') as infile:
            reader = csv.reader(infile, delimiter=';')
            next(reader, None)

            for row in reader:
                processed = process_row(row)
                if not processed:
                    writer.writerow(row)
                    continue

                identifier, unit_name = processed
                # Replace _2 name with _1 name
                if identifier.endswith('_2'):
                    base_id = identifier[:-2]
                    if base_id in unit_names:
                        unit_name = unit_names[base_id]

                writer.writerow([identifier, unit_name])

    # Remove original and rename temp to original
    os.replace(temp_output_path, input_path)
    print(f"Successfully updated: {input_path.name}")

def main():
    root = tk.Tk()
    root.withdraw()

    # Select files
    files = filedialog.askopenfilenames(
        title="Select CSV Files to Update",
        filetypes=[("CSV files", "*.csv")]
    )

    if not files:
        print("No files selected.")
    else:
        print(f"Selected {len(files)} file(s). Starting update...\n")
        for file_path in files:
            try:
                process_single_file(file_path)
            except Exception as e:
                print(f"CRITICAL ERROR in {Path(file_path).name}: {e}")

    print("\n" + "="*30)
    print("Process finished.")
    input("Press Enter to close this window...") # Keeps window open

if __name__ == "__main__":
    main()