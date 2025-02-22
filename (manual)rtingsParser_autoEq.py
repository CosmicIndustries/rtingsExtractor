import re
from bs4 import BeautifulSoup
import pandas as pd

def extract_and_clean_rtings_data(html_file, output_file):
    """Parses an RTINGS.com HTML file, extracts frequency response data, applies AutoEQ-style correction, and saves it in a format suitable for JamesDSP."""
    
    # Load the HTML file
    with open(html_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "lxml")
    
    # Extract frequency data (table)
    table = soup.find("table")
    if not table:
        print("No table found in the HTML file.")
        return
    
    # Extract table headers to see how many columns we have
    headers = [th.get_text(strip=True) for th in table.find_all("th")]
    print(f"Table headers: {headers}")  # Debug print for headers
    
    # Extract and clean frequency and gain data directly from rows
    rows = []
    for tr in table.find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) >= 4:
            freq = clean_number(cells[0].get_text())  # Frequency
            target = clean_number(cells[1].get_text())  # Harman Target
            avg_response = clean_number(cells[3].get_text())  # Average Response (raw data)
            if freq is not None and target is not None and avg_response is not None:
                rows.append((freq, target, avg_response))
    
    if not rows:
        print("No valid data found in the table.")
        return

    print(f"Extracted {len(rows)} rows of data:")
    print(rows)  # Debug print to check raw extracted data
    
    # Sort the data only once
    rows.sort(key=lambda x: x[0])  # Sort by frequency
    
    # Apply EQ correction
    eq_data = apply_eq_correction(rows)
    
    # Save the corrected data in GraphicEQ format (TXT)
    save_graphic_eq_format(eq_data, output_file)
    
    print(f"Cleaned and corrected data saved to {output_file}")

def clean_number(value):
    """Cleans the value and returns it as a float or None if invalid."""
    if isinstance(value, (int, float)):  # Already a number
        return float(value)
    if not value or value.strip() == "":  # Empty values
        return None
    num = re.sub(r"[^\d.-]", "", value)  # Remove non-numeric characters
    try:
        return float(num)
    except ValueError:
        return None  # Return None if conversion fails

def apply_eq_correction(data):
    """Applies EQ correction based on the difference between raw data and target curve."""
    corrected_data = []
    
    for f, target, avg_response in data:
        # Subtract the raw frequency response from the target (Harman curve)
        eq_gain = target - avg_response
        
        # Scale the result to fit within the range -32 to 32
        eq_gain = scale_gain(eq_gain)
        
        corrected_data.append((f, eq_gain))
    
    return corrected_data

def scale_gain(gain):
    """Scales the gain to the range -32 to 32."""
    # Use a linear scaling technique based on the actual data's min/max range
    # Here we will just limit the values to -32 to 32 for simplicity
    return max(-32, min(32, gain))

def save_graphic_eq_format(eq_data, output_file):
    """Saves the corrected EQ data in GraphicEQ format."""
    with open(output_file, "w", encoding="utf-8") as file:
        # Format output in the desired structure: GraphicEQ: 0 26.81; 54 26.82; ...
        eq_string = "GraphicEQ: " + "; ".join([f"{int(f)} {g:.2f}" for f, g in eq_data])
        file.write(eq_string)
        file.write("\n")

if __name__ == "__main__":
    # Replace with actual file paths
    input_html = "/storage/emulated/0/Download/Soundbar.html"  # Input HTML file
    output_txt = "/storage/emulated/0/Download/graphic_eq_output.txt"   # Output file for GraphicEQ
    extract_and_clean_rtings_data(input_html, output_txt)
