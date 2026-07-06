import os
import csv
from typing import Dict, Any

def generate_csv_report(filename: str, report_data: dict) -> str:
    """
    Serializes a report dictionary into a CSV table representation.
    Saves and returns the output absolute file path.
    """
    # Create directory if not exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Loop through each section
        for section_title, data in report_data.items():
            if not data:
                continue
            
            writer.writerow([f"=== {section_title} ==="])
            
            if isinstance(data, dict):
                for k, v in data.items():
                    label = str(k).replace("_", " ").title()
                    writer.writerow([label, str(v)])
                writer.writerow([]) # Empty row separator
                
            elif isinstance(data, list):
                if not data:
                    writer.writerow(["No records found."])
                    writer.writerow([])
                    continue
                    
                headers = list(data[0].keys())
                display_headers = [str(h).replace("_", " ").title() for h in headers]
                writer.writerow(display_headers)
                
                for row in data:
                    writer.writerow([str(row[h]) for h in headers])
                writer.writerow([]) # Empty row separator

    return os.path.abspath(filename)
