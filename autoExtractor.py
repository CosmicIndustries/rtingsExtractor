import re
import os
from bs4 import BeautifulSoup
import pandas as pd

def extract_and_clean_rtings_data(html_file, output_file):
    """
    Parses an RTINGS.com HTML file, extracts frequency response data,
    applies AutoEQ-style correction, and saves it in a format suitable for JamesDSP.
    """
    
    # Load and parse the HTML file
    if not os.path.exists(html_file):
        print(f"Error: File '{html_file}' not found.")
        return
    
    with open(html_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "lxml")
    
    # Locate the data table
    table = soup.find("table")
    if not table:
        print("No table found in the HTML file.")
        return
    
    # Extract column headers for reference
    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    print(f"Table Headers Found: {headers}")  # Debugging print

    # Extract frequency, target, and average response data
    rows = []
    for tr in table.find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) >= 4:  # Ensuring at least 4 columns exist
            freq = clean_number(cells[0].get_text())  # Frequency
            target = clean_number(cells[1].get_text())  # Harman Target
            avg_response = clean_number(cells[3].get_text())  # Average Response (raw data)
            
            # Only append valid numerical rows
            if freq is not None and target is not None and avg_response is not None:
                rows.append((freq, target, avg_response))
    
    if not rows:
        print("Error: No valid frequency response data extracted.")
        return

    print(f"Extracted {len(rows)} data points.")  # Debugging print

    # Ensure the data is sorted by frequency
    rows.sort(key=lambda x: x[0])

    # Apply EQ correction (AutoEQ)
    eq_data = apply_eq_correction(rows)

    # Save the corrected EQ data to a file
    with open(output_file, "w", encoding="utf-8") as file:
        file.writelines([f"{f} {g}\n" for f, g in eq_data])

    print(f"Processed data successfully saved to: {output_file}")

def clean_number(value):
    """
    Cleans a given string or number and returns it as a float.
    Returns None if the value is invalid.
    """
    if isinstance(value, (int, float)):  # Already numeric
        return float(value)
    if not value or value.strip() == "":  # Empty value
        return None
    num = re.sub(r"[^\d.-]", "", value)  # Remove non-numeric characters
    try:
        return float(num)
    except ValueError:
        return None  # Return None if conversion fails

def apply_eq_correction(data):
    """
    Applies EQ correction based on the difference between the raw response and target curve.
    """
    corrected_data = []
    
    for freq, target, avg_response in data:
        # Compute the required EQ gain (Harman Target - Raw Response)
        eq_gain = target - avg_response

        # Scale the gain to fit within the range -32 to 32
        eq_gain = scale_gain(eq_gain)

        corrected_data.append((freq, eq_gain))

    return corrected_data

def scale_gain(gain):
    """
    Scales the computed gain to fit within the range -32 to 32.
    Ensures that no values exceed the defined limits.
    """
    return max(-32, min(32, gain))  # Clamps values within range

if __name__ == "__main__":
    """
    Main execution block allowing user input for file paths.
    """

    print("\n--- AutoEQ Script for RTINGS Data ---\n")

    # Allow user input for file locations
    user_input = input("Do you already have the RTINGS HTML file? (yes/no): ").strip().lower()

    if user_input == "no":
        print("\n1. Visit RTINGS.com and find your headphone's frequency response page.")
        print("2. Right-click, select 'Save As', and save the page as an HTML file.")
        print("3. Place the saved file in the same directory as this script.\n")
        exit("Restart this script after saving the HTML file.")

    input_html = input("Enter the path to your RTINGS HTML file: ").strip()
    output_txt = input("Enter the output filename (e.g., jamesdsp_eq.txt): ").strip()

    # Run extraction and correction
    extract_and_clean_rtings_data(input_html, output_txt)
