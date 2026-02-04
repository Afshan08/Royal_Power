import json
import time
import requests

def perform_search(query, base_url, headers):
    try:
        params = {'q': query, 'format': 'json', 'limit': 1}
        response = requests.get(base_url, params=params, headers=headers)
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        pass
    return None, None

def geocode_dealers(input_file="dealers.json"):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            dealers = json.load(f)
    except FileNotFoundError:
        print("dealers.json not found.")
        return

    base_url = "https://nominatim.openstreetmap.org/search"
    headers = {
        'User-Agent': 'RoyalPowerDealerLocator/1.0'
    }
    
    # Manual fixes for common ambiguous addresses in the dataset
    MANUAL_CORRECTIONS = {
        "KHOKAR MUHALLAH": "Khokhar Mohalla, Larkana",
        "Kacha Khu Road, Abdulhakeem": "Abdul Hakim, Pakistan",
        "Hasilpur Road, Adda Bakshan Khan": "Bakshan Khan, Pakistan",
        "Near Shell Pump, Bhakkar Road, Adda jahan Khan": "Jahan Khan, Pakistan",
        "Main ferozpur road, Bank Road Mojahid Road": "Mujahid Road, Lahore",
        "islamabad mall opp col Amanullah road main murree road bara kahu": "Bhara Kahu, Islamabad",
        "Joya road,Bure wala": "Burewala, Pakistan",
        "Block # 02 Exchange Road, Chichwatni": "Chichawatni, Pakistan",
        "Basket ball Ground Chishtian": "Chishtian, Pakistan",
        "Nawan Kot Road Choubara": "Choubara, Pakistan",
        "Kashmir road tehsi kalar syden chou khalsa ditt Rawalpindi": "Kallar Syedan, Rawalpindi",
        "Chishtian Road Near PSO Pump,Daharanwala": "Daharanwala, Pakistan",
        "By Pass Road Daherki": "Daharki, Pakistan",
        "Hub Sakran Road": "Hub, Balochistan",
        "Sakran Road , Hub House# 01 , Al Hussain Market": "Hub, Balochistan",
        "Qazi Street, Hub Chowki Sakran Road": "Hub, Balochistan"
    }
    
    updated_count = 0
    
    print(f"Starting geocoding for {len(dealers)} dealers...")
    print("Note: This uses OpenStreetMap (free). It requires 1 second delay between requests.")

    for i, dealer in enumerate(dealers):
        # Skip if already has coordinates
        if dealer.get('lat') is not None and dealer.get('lng') is not None:
            continue
            
        # Strategy 0: Manual Correction
        cleaned_address = dealer['address'].strip()
        if cleaned_address in MANUAL_CORRECTIONS:
            query = f"{MANUAL_CORRECTIONS[cleaned_address]}, Pakistan"
            print(f"  -> Using manual fix for: {cleaned_address}")
        elif "KHOKAR MUHALLAH" in cleaned_address: # Partial match for the cluster
             query = "Khokhar Mohalla, Larkana, Pakistan"
             print(f"  -> Using manual fix for Khokhar Mohalla")
        else:
            # Strategy 1: Full Address
            query = f"{cleaned_address}, Pakistan"
        
        lat, lng = perform_search(query, base_url, headers)
        
        # Strategy 2: Fallback to last part of address (often the city)
        if not lat and ',' in dealer['address']:
            city_part = dealer['address'].rsplit(',', 1)[-1].strip()
            if len(city_part) > 3: # Avoid short weird parts
                print(f"  -> Retrying with city fallback: {city_part}")
                query = f"{city_part}, Pakistan"
                lat, lng = perform_search(query, base_url, headers)

        # Strategy 3: Heuristic - Last 2 words (likely city if no commas)
        if not lat:
            words = dealer['address'].split()
            if len(words) >= 2:
                city_guess = f"{words[-2]} {words[-1]}"
                print(f"  -> Retrying with heuristic city: {city_guess}")
                query = f"{city_guess}, Pakistan"
                lat, lng = perform_search(query, base_url, headers)
            elif len(words) == 1:
                city_guess = words[0]
                print(f"  -> Retrying with single word city: {city_guess}")
                query = f"{city_guess}, Pakistan"
                lat, lng = perform_search(query, base_url, headers)

        if lat and lng:
            dealer['lat'] = lat
            dealer['lng'] = lng
            updated_count += 1
            print(f"[{i+1}/{len(dealers)}] Found: {dealer['name']} -> {lat}, {lng}")
        else:
            print(f"[{i+1}/{len(dealers)}] FAILED: {dealer['address']}")
            
        # Respect rate limit (1 second)
        time.sleep(1.1)
        
        # Save progress every 10 items
        if i % 10 == 0:
            with open(input_file, 'w', encoding='utf-8') as f:
                json.dump(dealers, f, indent=4)

    # Final save
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(dealers, f, indent=4)
        
    print(f"\nGeocoding complete. Updated {updated_count} dealers.")

if __name__ == "__main__":
    # Ensure requests is installed
    try:
        import requests
    except ImportError:
        print("Please install requests: pip install requests")
        exit()
        
    geocode_dealers()
