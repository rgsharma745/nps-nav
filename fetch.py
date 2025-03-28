import csv
import os
import zipfile
from datetime import datetime, timedelta
from io import BytesIO

import requests
import urllib3

# Disable SSL warnings since we're disabling verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DATE_FORMAT = '%m/%d/%Y'
DIRECT_IP = "144.126.254.118"
SCHEME_CODES = ["SM007001", "SM007002", "SM007003"]

def download_and_extract_nav(date_str, url_variations):
    """
    Attempt to download and extract the NAV data for a given date using multiple URL variations.
    Returns the extracted file name if successful, otherwise returns None.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Host': 'npscra.nsdl.co.in'
    }

    for variation in url_variations:
        domain_url = variation.format(date_str=date_str)
        ip_url = domain_url.replace('npscra.nsdl.co.in', DIRECT_IP)
        print(f"Trying URL: {ip_url}")

        try:
            response = requests.get(ip_url, headers=headers, verify=False, timeout=30)

            if response.status_code == 200:
                print(f"Successfully downloaded from: {ip_url}")
                try:
                    with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
                        for file_name in zip_ref.namelist():
                            if file_name.endswith('.out'):
                                zip_ref.extract(file_name, os.getcwd())
                                print(f"Extracted: {file_name}")
                                return file_name
                except zipfile.BadZipFile:
                    print(f"Invalid ZIP file received from {ip_url}")

            elif response.status_code == 404:
                print(f"NAV file not available at {ip_url}")
            else:
                print(f"Failed to download from {ip_url}. Status code: {response.status_code}")

        except requests.RequestException as e:
            print(f"Error downloading from {ip_url}: {e}")

    return None


def parse_out_file(file_name):
    """Parse the .out file and extract the NAV data."""
    data_list = []
    with open(file_name, 'r') as file:
        for line in file:
            columns = line.strip().split(',')
            if len(columns) == 6:
                scheme_data = {
                    "DATE": columns[0],
                    "PFM CODE": columns[1],
                    "PFM NAME": columns[2],
                    "SCHEME CODE": columns[3],
                    "SCHEME NAME": columns[4],
                    "NAV": columns[5]
                }
                data_list.append(scheme_data)
    return data_list


def update_csv(data):
    """Update individual JSON files for each scheme with the latest NAV data."""
    if not os.path.exists('data'):
        os.makedirs('data')

    with open("data/nav.csv", mode='w', newline='') as file:
        fieldnames = ['SCHEME CODE', 'SCHEME NAME', 'NAV', 'DATE']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            if row['SCHEME CODE'] in SCHEME_CODES:
                writer.writerow({
                    'SCHEME CODE': row['SCHEME CODE'],
                    'SCHEME NAME': row['SCHEME NAME'],
                    'NAV': row['NAV'],
                    'DATE': row['DATE']
                })


def clean_up(file_name):
    """Delete the extracted .out file to clean up."""
    if os.path.exists(file_name):
        os.remove(file_name)
        print(f"Deleted {file_name}")


def process_date(date, url_variations):
    """Process a single date: download, extract, parse, and update data."""
    date_str = date.strftime("%d%m%Y")
    print(f"Trying to fetch NAV data for {date.strftime('%d-%m-%Y')}...")
    out_file = download_and_extract_nav(date_str, url_variations)
    if out_file:
        nav_data = parse_out_file(out_file)
        update_csv(nav_data)
        clean_up(out_file)
    else:
        print(f"No NAV data available for {date.strftime('%d-%m-%Y')}.")


def last_working_day(days_to_minus):
    today = datetime.today()
    day_of_week = today.weekday()
    if day_of_week == 6:
        last_working_date = today - timedelta(days=2 + days_to_minus)
    elif day_of_week == 5:
        last_working_date = today - timedelta(days=1 + days_to_minus)
    else:
        last_working_date = today - timedelta(days=1 + days_to_minus)
    return last_working_date


if __name__ == "__main__":
    url_variations = [
        "https://npscra.nsdl.co.in/download/NAV_File_{date_str}.zip",
        "https://npscra.nsdl.co.in/download/NAV_FILE_{date_str}.zip",
        "https://npscra.nsdl.co.in/download/NAV_file_{date_str}.zip",
        "https://npscra.nsdl.co.in/download/NAV%20File%20{date_str}.zip",
        "https://npscra.nsdl.co.in/download/NAV%20FILE%20{date_str}.zip",
        "https://npscra.nsdl.co.in/download/nav%20file%20{date_str}.zip"
    ]

    try:
        process_date(last_working_day(1), url_variations)
        process_date(last_working_day(0), url_variations)
        process_date(datetime.now(), url_variations)
    except Exception as exc:
        print(f"Generated an exception: {exc}")
