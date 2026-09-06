import requests
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

def fetch_nps_nav():
    base_url = os.getenv("NAV_API_URL").rstrip("/")
    token = os.getenv("NAV_API_TOKEN")

    headers = {"Authorization": f"Bearer {token}"} if token else {}
    current_date = datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()
    nav_data = {}
    response_dates = set()

    try:
        for tier in ("tier1_g", "tier1_e", "tier1_c"):
            url = f"{base_url}/{current_date}/{current_date}/{tier}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            latest_data = response.json()["latest_data"]
            nav_data[tier] = latest_data["final_value"]
            response_dates.add(latest_data["date"])

        if len(response_dates) != 1:
            raise ValueError("NAV responses returned different dates")
        nav_date = response_dates.pop()

        data = {
            tier: {"date": nav_date, "nav": nav}
            for tier, nav in nav_data.items()
        }

        with open("data/nav.json", "w") as nav_file:
            json.dump(data, nav_file, indent=2)
            nav_file.write("\n")

        print(f"Successfully downloaded NAV data for {current_date} IST")
        print(json.dumps(nav_data, indent=2))
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
