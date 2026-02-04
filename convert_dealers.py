import json
import os

def parse_dealer_data(file_path):
    dealers = []
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    i = 0
    while i < len(lines):
        name = lines[i]
        
        # Skip empty lines to find the next name
        if not name:
            i += 1
            continue
            
        # Ensure there is a next line for address/contact
        if i + 1 < len(lines):
            details_line = lines[i+1]
            
            # Default values
            address = details_line
            phone = "N/A"
            contact_person = ""
            
            # Try to split by comma if present
            # Example: "Address , Contact Phone"
            if ',' in details_line:
                parts = details_line.rsplit(',', 1) # Split from right to separate last part
                address = parts[0].strip()
                contact_part = parts[1].strip()
                
                # Try to extract phone number from contact part (simplified)
                # Assuming format like "Mr.Khawar Khan 923336454041"
                # We can just store the whole string as contact/phone or try to split
                phone = contact_part
            
            dealer = {
                "name": name,
                "address": address,
                "phone": phone,
                "lat": None, # Data doesn't have coordinates
                "lng": None
            }
            dealers.append(dealer)
            
            # Move index past name and details
            i += 2 
        else:
            # End of file or malformed last record
            break
            
    return dealers

if __name__ == "__main__":
    input_file = "data.txt"
    output_file = "dealers.json"
    
    dealers = parse_dealer_data(input_file)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dealers, f, indent=4)
        
    print(f"Successfully converted {len(dealers)} dealers to {output_file}")
