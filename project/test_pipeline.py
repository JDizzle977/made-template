import os
import subprocess
import pandas as pd
import sqlite3

DATA_DIR = "../data"
DB_FILE = os.path.join(DATA_DIR, "storm_gdb_analysis.db")
REQUIRED_COLUMNS_NOAA = [
    "EVENT_ID", "STATE", "MONTH_NAME", "EVENT_TYPE", "BEGIN_DATE_TIME", "END_DATE_TIME",
    "INJURIES_DIRECT", "INJURIES_INDIRECT", "DEATHS_DIRECT", "DEATHS_INDIRECT",
    "DAMAGE_PROPERTY", "DAMAGE_CROPS", "SOURCE", "BEGIN_LOCATION", "END_LOCATION",
    "EPISODE_NARRATIVE", "DATA_SOURCE"
]


def test_pipeline_execution():
    """
    Tests, whether the pipeline executes successfully without throwing an exception.
    """
    result = subprocess.run(["python", "pipeline.py"], capture_output=True, text=True)
    assert result.returncode == 0, f"Pipeline failed: {result.stderr}"
    print("\t\tPipeline executed successfully.")

def test_storm_event_files():
    """
    Tests, whether the storm event files have been created.
    """
    storm_event_dir = os.path.join(DATA_DIR, "storm_event_files")
    assert os.path.isdir(storm_event_dir), f"Directory {storm_event_dir} does not exist."
    files = os.listdir(storm_event_dir)
    assert len(files) > 0, "No files were downloaded for storm events."
    print(f"\t\tFound {len(files)} storm event files.")

def test_storm_event_combined_file():
    """
    Tests, whether the single yearly storm event files could've been combined to a single XLSX-File.
    """
    combined_file = os.path.join(DATA_DIR, "storm_event_ds_combined", "storm_event_ds_combined.xlsx")
    assert os.path.isfile(combined_file), f"Combined Excel-File {combined_file} does not exist."

    excel_data = pd.ExcelFile(combined_file)
    assert len(excel_data.sheet_names) > 0, "Combined Excel-File has no sheets."


def test_storm_event_columns():
    """
    Tests whether the combined Excel file contains exactly the required columns. Assumes the existance of the combined Excel File
    """
    combined_file = os.path.join(DATA_DIR, "storm_event_ds_combined", "storm_event_ds_combined.xlsx")
    excel_data = pd.ExcelFile(combined_file)

    for sheet_name in excel_data.sheet_names:
        df = excel_data.parse(sheet_name)

        missing_columns = [col for col in REQUIRED_COLUMNS_NOAA if col not in df.columns]
        extra_columns = [col for col in df.columns if col not in REQUIRED_COLUMNS_NOAA]

        assert not missing_columns, f"Missing columns in sheet {sheet_name}: {missing_columns}"
        assert not extra_columns, f"Extra columns found in sheet {sheet_name}: {extra_columns}"


def test_bea_gdp_file():
    """
    Tests, whether the BEA-Data could have been downloaded and extracted correctly.
    """
    bea_gdp_dir = os.path.join(DATA_DIR, "bea_gdp")
    assert os.path.isdir(bea_gdp_dir), f"Directory {bea_gdp_dir} does not exist."
    files = [f for f in os.listdir(bea_gdp_dir) if f.endswith(".csv")]
    assert len(files) > 0, "No BEA GDP CSV file found."



################# Database Checks #################

def test_db_file_exists():
    """
    Test, whether the SQLite database file exists.
    """
    assert os.path.isfile(DB_FILE), f"Database {DB_FILE} does not exist."

def test_db_tables_exist():
    """
    Test, whether the database contains tables corresponding to all sheets in the Excel file.
    """
    combined_file = os.path.join(DATA_DIR, "storm_event_ds_combined", "storm_event_ds_combined.xlsx")
    excel_data = pd.ExcelFile(combined_file)
    expected_tables = excel_data.sheet_names

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    db_tables = [row[0] for row in cursor.fetchall()]

    missing_tables = [table for table in expected_tables if table not in db_tables]
    assert not missing_tables, f"Missing tables in database: {missing_tables}"

    conn.close()

def test_db_columns():
    """
    Test, whether each table in the database contains the required columns for the storm events.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    combined_file = os.path.join(DATA_DIR, "storm_event_ds_combined", "storm_event_ds_combined.xlsx")
    excel_data = pd.ExcelFile(combined_file)
    expected_tables = excel_data.sheet_names

    for table in expected_tables:
        cursor.execute(f"PRAGMA table_info({table});")
        db_columns = [row[1] for row in cursor.fetchall()]  # index 0 -> tables, index 1 -> column names
        print(table)
        missing_columns = [col for col in REQUIRED_COLUMNS_NOAA if col not in db_columns]
        extra_columns = [col for col in db_columns if col not in REQUIRED_COLUMNS_NOAA and col != 'sheet_name']

        assert not missing_columns, f"Missing columns in table {table}: {missing_columns}"
        assert not extra_columns, f"Extra columns found in table {table}: {extra_columns}"

    conn.close()

def test_db_data_integrity():
    """
    Test, whether each table in the database contains data.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    combined_file = os.path.join(DATA_DIR, "storm_event_ds_combined", "storm_event_ds_combined.xlsx")
    excel_data = pd.ExcelFile(combined_file)
    expected_tables = excel_data.sheet_names

    for table in expected_tables:
        cursor.execute(f"SELECT COUNT(*) FROM \"{table}\";")            # As the sheet names and also the table names are called by the year ->
                                                                        # Escape of the Number by quotes necessary
        row_count = cursor.fetchone()[0]
        assert row_count > 0, f"{table} contains no data."

        print(f"{table} contains {row_count} rows.")

    conn.close()