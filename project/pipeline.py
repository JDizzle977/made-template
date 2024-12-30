import os
import re
import platform
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
import sqlite3

urls = {
    "NOAA": "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/",
    "BEA": "https://apps.bea.gov/itable/?ReqID=70&step=1#eyJhcHBpZCI6NzAsInN0ZXBzIjpbMSwyOSwyNSwzMSwyNiwyNywzMF0sImRhdGEiOltbIlRhYmxlSWQiLCI2MDAiXSxbIk1ham9yX0FyZWEiLCIwIl0sWyJTdGF0ZSIsWyIwIl1dLFsiQXJlYSIsWyJYWCJdXSxbIlN0YXRpc3RpYyIsWyItMSJdXSxbIlVuaXRfb2ZfbWVhc3VyZSIsIlBlcmNlbnRDaGFuZ2UiXSxbIlllYXIiLFsiLTEiXV0sWyJZZWFyQmVnaW4iLCItMSJdLFsiWWVhcl9FbmQiLCItMSJdXX0="
}

data_dir = "../data"


def download_and_extract_storm_event_files(url, download_dir=data_dir + '/storm_event_files'):
    os.makedirs(download_dir, exist_ok=True)

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


def filter_columns(dataframe, columns_to_keep):
    available_columns = [col for col in columns_to_keep if col in dataframe.columns]
    return dataframe[available_columns]

def csvs_to_excel(input_dir, output_file):

    required_columns = [
        "EVENT_ID", "STATE", "MONTH_NAME", "EVENT_TYPE", "BEGIN_DATE_TIME", "END_DATE_TIME",
        "INJURIES_DIRECT", "INJURIES_INDIRECT", "DEATHS_DIRECT", "DEATHS_INDIRECT",
        "DAMAGE_PROPERTY", "DAMAGE_CROPS", "SOURCE", "BEGIN_LOCATION", "END_LOCATION",
        "EPISODE_NARRATIVE", "DATA_SOURCE"
    ]

    with pd.ExcelWriter(output_file) as writer:
        for file in os.listdir(input_dir):
            if file.endswith(".csv"):
                print(file)
                year = re.search(r'_d(\d{4})_', file).group(1)  # extracting the year from the filename
                print(year)
                df = pd.read_csv(os.path.join(input_dir, file))
                df = filter_columns(df, required_columns)
                df.to_excel(writer, sheet_name=year, index=False)


def download_bea_gdp_csv(url):
    download_dir = os.path.join(data_dir, 'bea_gdp')
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument(f"--headless")  # Setting browser to the background

    # Changing the download path of selenium-chrome to bea_gdp inside data_dir
    prefs = {"download.default_directory": os.path.abspath(download_dir)}
    chrome_options.add_experimental_option("prefs", prefs)

    # Dynamically setting the ChromeDriver path based on OS such that the Github-Pipeline on ubuntu doesnt fail
    if platform.system() == "Windows":
        driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
    elif platform.system() == "Linux":
        driver_path = "/usr/local/bin/chromedriver" 
    else:
        raise OSError(f"Scotty, wir haben ein Problem. Das OS ist unbekannt! {platform.system()}.")


    #driver_path = os.path.join(os.getcwd(), 'chromedriver.exe')

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


def storm_events_to_sqlite(excel_file, db_file):
    excel_data = pd.ExcelFile(excel_file)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        for sheet_name in excel_data.sheet_names:

            df = excel_data.parse(sheet_name)

            df['sheet_name'] = sheet_name

            df.to_sql(sheet_name, conn, if_exists='replace', index=False)

            print(f"Successfully written sheet '{sheet_name}' to database.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        conn.close()
        print("Database connection closed.")


def clean_bea_gdp_csv(file_path):
    df = pd.read_csv(file_path, skiprows=3)

    df = df.drop(df.columns[0], axis=1)

    # creating new file
    base_name = os.path.basename(file_path)
    dir_name = os.path.dirname(file_path)
    clean_file_name = f"cleaned_{base_name}"
    clean_file_path = os.path.join(dir_name, clean_file_name)

    # saving cleaned file
    df.to_csv(clean_file_path, index=False)

    print(f"Cleaned data saved to {clean_file_path}")

    return clean_file_path


def create_and_fill_bea_db(cleaned_file_path, db_name="gdp_data.db"):

    df = pd.read_csv(cleaned_file_path)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Creating a table for the GeoNames -> United States, Alabama, ...
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS GeoNames (
            GeoNameID INTEGER PRIMARY KEY AUTOINCREMENT,
            GeoName TEXT UNIQUE
        )
        ''')

    # Creating a table for the Indicators -> Real GDP, Real personal income, ...
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Indicators (
            IndicatorID INTEGER PRIMARY KEY AUTOINCREMENT,
            LineCode REAL,
            Description TEXT UNIQUE
        )
        ''')

    # Creating a table for the data -> 1999 +4.8 increase of GDP, ...
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS GDPData (
            GDPDataID INTEGER PRIMARY KEY AUTOINCREMENT,
            GeoNameID INTEGER,
            IndicatorID INTEGER,
            Year INTEGER,
            Value REAL,
            FOREIGN KEY (GeoNameID) REFERENCES GeoNames(GeoNameID),
            FOREIGN KEY (IndicatorID) REFERENCES Indicators(IndicatorID)
        )
        ''')

    # Making the GeoName table values unique, as they can be used multiple times due to foreign key association
    geo_names = df["GeoName"].unique()
    cursor.executemany('INSERT OR IGNORE INTO GeoNames (GeoName) VALUES (?)',
                       [(name,) for name in geo_names])

    # Indicators also repeat for each category -> thus can also be made unique
    indicators = df[["LineCode", "Description"]].drop_duplicates()
    cursor.executemany('INSERT OR IGNORE INTO Indicators (LineCode, Description) VALUES (?, ?)',
                       indicators.values)

    # Transform the DF to long format for year-value pairs
    df_long = df.melt(id_vars=["GeoName", "LineCode", "Description"],
                      var_name="Year",
                      value_name="Value")

    # Verification that year is of the type integer plus handling missing values
    df_long["Year"] = df_long["Year"].astype(int, errors='ignore')
    df_long["Value"] = pd.to_numeric(df_long["Value"], errors='coerce')

    # Mapping GeoNames and Indicators to their IDs
    geo_name_map = {row[1]: row[0] for row in cursor.execute('SELECT GeoNameID, GeoName FROM GeoNames')}
    indicator_map = {row[1]: row[0] for row in cursor.execute('SELECT IndicatorID, LineCode FROM Indicators')}

    df_long["GeoNameID"] = df_long["GeoName"].map(geo_name_map)
    df_long["IndicatorID"] = df_long["LineCode"].map(indicator_map)

    # Inserting the data into GDPData table
    gdp_data = df_long[["GeoNameID", "IndicatorID", "Year", "Value"]].dropna()
    gdp_data.to_sql("GDPData", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()

    print(f"Database {db_name} created and populated successfully.")


def main():
    print('If the subdirectories of data_dir are not empty, the script assumes necessary data already is available! -> Clear them if data is inconsistent/broken and restart the shell-script.')

    storm_event_files_dir = os.path.join(data_dir, 'storm_event_files')
    combined_storm_events_dir = os.path.join(data_dir, 'storm_event_ds_combined')
    bea_gdp_dir = os.path.join(data_dir, 'bea_gdp')

    for directory in [storm_event_files_dir, combined_storm_events_dir, bea_gdp_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"Created missing directory: {directory}")

    if not os.listdir(storm_event_files_dir):
        print(f"Processing: {storm_event_files_dir} is either empty or newly created.")
        download_and_extract_storm_event_files(urls["NOAA"])

    if not os.listdir(combined_storm_events_dir):
        print(f"Processing: {combined_storm_events_dir} is either empty or newly created.")
        csvs_to_excel(storm_event_files_dir, os.path.join(combined_storm_events_dir, 'storm_event_ds_combined.xlsx'))

    # Converting the Storm Data from an Excel-File to an sqlite-DB
    sqlite_db_path = "../data/storm_gdb_analysis.db"
    storm_events_combined_file = os.path.join(combined_storm_events_dir, 'storm_event_ds_combined.xlsx')

    if not os.path.exists(sqlite_db_path):
        print(f"SQLite database not found -> Converting {storm_events_combined_file} to SQLite db.")
        storm_events_to_sqlite(storm_events_combined_file, sqlite_db_path)
    else:
        print(f"SQLite database {sqlite_db_path} already exists -> Skipping processing.")


    if not os.listdir(bea_gdp_dir):
        print(f"Processing: {bea_gdp_dir} is either empty or newly created.")
        download_bea_gdp_csv(urls["BEA"])

    input_file = os.path.join(bea_gdp_dir, 'Table.csv')
    cleaned_file = os.path.join(bea_gdp_dir, 'cleaned_Table.csv')

    if not os.path.exists(cleaned_file):
        print(f"Cleaned file not found -> Processing {input_file}.")
        clean_bea_gdp_csv(input_file)
    else:
        print(f"Cleaned file {cleaned_file} already exists -> Skipping processing.")

    bea_gdp_db_path = os.path.join(data_dir, 'gdp_data.db')
    if not os.path.exists(bea_gdp_db_path):
       create_and_fill_bea_db(cleaned_file, bea_gdp_db_path)
    else:
        print(f"Database {bea_gdp_db_path} already exists -> No creation of the database necessary")


if __name__ == "__main__":
    main()