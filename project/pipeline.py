import os
import re

import requests
from bs4 import BeautifulSoup
import gzip
import shutil
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

urls = {
    "NOAA": "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/",
    "BEA": "https://apps.bea.gov/itable/?ReqID=70&step=1#eyJhcHBpZCI6NzAsInN0ZXBzIjpbMSwyOSwyNSwzMSwyNiwyNywzMF0sImRhdGEiOltbIlRhYmxlSWQiLCI2MDAiXSxbIk1ham9yX0FyZWEiLCIwIl0sWyJTdGF0ZSIsWyIwIl1dLFsiQXJlYSIsWyJYWCJdXSxbIlN0YXRpc3RpYyIsWyItMSJdXSxbIlVuaXRfb2ZfbWVhc3VyZSIsIlBlcmNlbnRDaGFuZ2UiXSxbIlllYXIiLFsiLTEiXV0sWyJZZWFyQmVnaW4iLCItMSJdLFsiWWVhcl9FbmQiLCItMSJdXX0="
}

data_dir = "../data"


def download_and_extract_storm_event_files(url, download_dir=data_dir + '/storm_event_files'):

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Request Error for the Parameter-URL: {response.status_code}")
        return

    # Parse Url
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links on the page
    links = soup.find_all('a', href=True)

    # Filter urls starting with 'StormEvents_details-ftp_v1.0' and ending with '.csv.gz'
    files_to_download = [
        link['href'] for link in links
        if link['href'].startswith('StormEvents_details-ftp_v1.0') and link['href'].endswith('.csv.gz')
           and any('d'+str(year) in link['href'] for year in range(1999, 2025))  # Filter for year
    ]
    if not files_to_download:
        print("Filtered Links not found.")
        return

    # Downloading and extracting files
    for file in files_to_download:
        file_url = url + file
        print(f"Downloading File: {file_url}")

        # request for downloading the yearly storm event
        file_response = requests.get(file_url)

        # check whether download was successful
        if file_response.status_code == 200:
            gz_file_path = os.path.join(download_dir, file.split('/')[-1])
            csv_file_path = os.path.join(download_dir, file.split('/')[-1].replace('.gz', ''))

            # saving .gz file
            with open(gz_file_path, 'wb') as gz_file:
                gz_file.write(file_response.content)
            print(f"Successfully Downloaded: {gz_file_path}")

            # Extraction of the csv inside the gz file
            with gzip.open(gz_file_path, 'rb') as f_in:
                with open(csv_file_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(f"Successfully Extracted: {csv_file_path}")

            # Delete .gz-files after extraction
            os.remove(gz_file_path)
            print(f"GZ-File removed: {gz_file_path}")

        else:
            print(f"Download Request failed: {file_url}")


def csvs_to_excel(input_dir, output_file):
    with pd.ExcelWriter(output_file) as writer:
        for file in os.listdir(input_dir):
            if file.endswith(".csv"):
                print(file)
                year = re.search(r'_d(\d{4})_', file).group(1)  # extracting the year from the filename
                print(year)
                df = pd.read_csv(os.path.join(input_dir, file))
                df.to_excel(writer, sheet_name=year, index=False)


def download_bea_gdp_csv(url):
    download_dir = os.path.join(data_dir, 'bea_gdp')
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument(f"--headless")  # Setting browser to the background

    # Changing the download path of selenium-chrome to bea_gdp inside data_dir
    prefs = {"download.default_directory": os.path.abspath(download_dir)}
    chrome_options.add_experimental_option("prefs", prefs)

    driver_path = os.path.join(os.getcwd(), 'chromedriver.exe')

    service = Service(driver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)

    try:
        download_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "DownloadTableBtn"))
        )
        print("Download button found")
        download_button.click()

        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "download-modal-Body"))
        )
        print("Download modal is visible")

        element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick, \"DoDownload('csv')\")]"))
        )
        print("CSV download button found")
        element.click()

        # wait till download is completed
        time.sleep(5)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

def main():
    print('stuff')
    storm_event_files_dir = os.path.join(data_dir, 'storm_event_files')
    if not os.listdir(storm_event_files_dir):
        download_and_extract_storm_event_files(urls["NOAA"])

    combined_storm_events_dir = os.path.join(data_dir, 'storm_event_ds_combined')
    if not os.listdir(combined_storm_events_dir):
        csvs_to_excel(storm_event_files_dir, data_dir + '/storm_event_ds_combined/storm_event_ds_combined.xlsx')
    bea_gdp_dir = os.path.join(data_dir, 'bea_gdp')

    if not os.listdir(bea_gdp_dir):
        download_bea_gdp_csv(urls["BEA"])

if __name__ == "__main__":
    main()