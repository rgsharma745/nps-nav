import requests
import json
import os
from datetime import datetime

def fetch_nps_nav():
    url = os.getenv("NAV_API_URL")
    token = os.getenv("NAV_API_TOKEN")
    
    if not token:
        raise ValueError("NAV_API_TOKEN environment variable is not set")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()  # Raise exception for bad status codes
        
        data = response.json()
        print(f"Successfully downloaded NAV data at {datetime.now()}")
        print(json.dumps(data, indent=2))
        
        # Optionally save to file
        with open("data/nav.json", "w") as f:
            json.dump(data, f, indent=2)
        print("Data saved to data/nav.json")
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"Failed to download NAV: {e}")
        raise

if __name__ == "__main__":
    try:
        fetch_nps_nav()
    except Exception as exc:
        print(f"Generated an exception: {exc}")
