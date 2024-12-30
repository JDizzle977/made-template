import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


def load_storm_events_data(db_path):
    conn = sqlite3.connect(db_path)

    years = range(1999, 2025)

    storm_data_frames = []

    for year in years:
        table_name = str(year)

        query = f"""
        SELECT STATE,
               SUM(CASE 
                       WHEN DAMAGE_PROPERTY LIKE '%K' THEN REPLACE(DAMAGE_PROPERTY, 'K', '') * 1000
                       WHEN DAMAGE_PROPERTY LIKE '%M' THEN REPLACE(DAMAGE_PROPERTY, 'M', '') * 1000000
                       ELSE REPLACE(DAMAGE_PROPERTY, ',', '') 
                   END +
               CASE 
                       WHEN DAMAGE_CROPS LIKE '%K' THEN REPLACE(DAMAGE_CROPS, 'K', '') * 1000
                       WHEN DAMAGE_CROPS LIKE '%M' THEN REPLACE(DAMAGE_CROPS, 'M', '') * 1000000
                       ELSE REPLACE(DAMAGE_CROPS, ',', '') 
               END) AS total_damage
        FROM "{table_name}"
        GROUP BY STATE
        """

        df_year = pd.read_sql(query, conn)

        df_year['YEAR'] = year

        storm_data_frames.append(df_year)

    storm_data = pd.concat(storm_data_frames, ignore_index=True)

    conn.close()
    return storm_data


def load_bea_gdp_data(db_path):
    conn = sqlite3.connect(db_path)

    query = """
    SELECT
        UPPER(GeoNames.GeoName) AS State,
        GDPData.Year,
        GDPData.Value AS GDP,
        Indicators.Description AS Indicator
    FROM GDPData
    JOIN GeoNames ON GDPData.GeoNameID = GeoNames.GeoNameID
    JOIN Indicators ON GDPData.IndicatorID = Indicators.IndicatorID
    WHERE GDPData.IndicatorID = 2
    """

    gdp_data = pd.read_sql(query, conn)

    conn.close()
    return gdp_data


def calculate_correlations(storm_data, gdp_data):
    states = storm_data['STATE'].unique()
    correlations = {}

    for state in states:
        storm_data_state = storm_data[storm_data['STATE'] == state]

        gdp_data_state = gdp_data[gdp_data['State'] == state]

        annual_damage = storm_data_state.groupby('YEAR')['total_damage'].sum().reset_index()

        merged_data = pd.merge(annual_damage, gdp_data_state, left_on="YEAR", right_on="Year")

        correlation = merged_data[['total_damage', 'GDP']].corr().iloc[0, 1]
        correlations[state] = correlation

    return correlations


def get_extreme_correlation_states(correlations):
    negative_correlation_state = min(correlations, key=correlations.get)

    positive_correlation_state = max(correlations, key=correlations.get)

    return negative_correlation_state, positive_correlation_state


def plot_extreme_states(storm_data, gdp_data, negative_state, positive_state):
    storm_data_negative, gdp_data_negative = filter_data_for_state(storm_data, gdp_data, negative_state)
    storm_data_positive, gdp_data_positive = filter_data_for_state(storm_data, gdp_data, positive_state)

    annual_damage_negative = storm_data_negative.groupby('YEAR')['total_damage'].sum().reset_index()
    annual_damage_positive = storm_data_positive.groupby('YEAR')['total_damage'].sum().reset_index()

    merged_data_negative = pd.merge(annual_damage_negative, gdp_data_negative, left_on="YEAR", right_on="Year")
    merged_data_positive = pd.merge(annual_damage_positive, gdp_data_positive, left_on="YEAR", right_on="Year")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    ax1 = axes[0]
    ax1.set_xlabel('Year')
    ax1.set_ylabel('GDP', color='red')
    ax1.plot(merged_data_negative['YEAR'], merged_data_negative['GDP'], color='red', label='GDP', linewidth=2)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Total Damage', color='blue')
    ax2.plot(merged_data_negative['YEAR'], merged_data_negative['total_damage'], color='blue', label='Total Damage',
             linewidth=2)
    ax1.set_title(f'{negative_state} (Negative Correlation)')

    ax3 = axes[1]
    ax3.set_xlabel('Year')
    ax3.set_ylabel('GDP', color='red')
    ax3.plot(merged_data_positive['YEAR'], merged_data_positive['GDP'], color='red', label='GDP', linewidth=2)
    ax4 = ax3.twinx()
    ax4.set_ylabel('Total Damage', color='blue')
    ax4.plot(merged_data_positive['YEAR'], merged_data_positive['total_damage'], color='blue', label='Total Damage',
             linewidth=2)
    ax3.set_title(f'{positive_state} (Positive Correlation)')

    plt.tight_layout()
    plt.show()


def filter_data_for_state(storm_data, gdp_data, state_name):

    storm_data_state = storm_data[storm_data['STATE'] == state_name]

    gdp_data_state = gdp_data[gdp_data['State'] == state_name]

    return storm_data_state, gdp_data_state


def print_total_correlation_for_extreme_states(storm_data, gdp_data, negative_state, positive_state):

    storm_data_negative, gdp_data_negative = filter_data_for_state(storm_data, gdp_data, negative_state)

    storm_data_positive, gdp_data_positive = filter_data_for_state(storm_data, gdp_data, positive_state)

    annual_damage_negative = storm_data_negative.groupby('YEAR')['total_damage'].sum().reset_index()
    annual_damage_positive = storm_data_positive.groupby('YEAR')['total_damage'].sum().reset_index()

    merged_data_negative = pd.merge(annual_damage_negative, gdp_data_negative, left_on="YEAR", right_on="Year")
    merged_data_positive = pd.merge(annual_damage_positive, gdp_data_positive, left_on="YEAR", right_on="Year")

    total_correlation_negative = merged_data_negative[['total_damage', 'GDP']].corr().iloc[0, 1]
    print(f"Total Correlation for {negative_state} (Negative Correlation State) over all years: {total_correlation_negative}")

    total_correlation_positive = merged_data_positive[['total_damage', 'GDP']].corr().iloc[0, 1]
    print(f"Total Correlation for {positive_state} (Positive Correlation State) over all years: {total_correlation_positive}")

def calculate_total_correlation(storm_data, gdp_data):

    total_damage = storm_data.groupby('YEAR')['total_damage'].sum().reset_index()

    total_gdp = gdp_data.groupby('Year')['GDP'].sum().reset_index()

    merged_data_total = pd.merge(total_damage, total_gdp, left_on="YEAR", right_on="Year")

    total_correlation = merged_data_total[['total_damage', 'GDP']].corr().iloc[0, 1]
    print(f"Total Correlation for all states over all years: {total_correlation}")

    return merged_data_total


def plot_total_correlation(merged_data_total):
    plt.figure(figsize=(8, 6))
    plt.plot(merged_data_total['YEAR'], merged_data_total['GDP'], color='red', label='GDP', linewidth=2)
    plt.twinx()
    plt.plot(merged_data_total['YEAR'], merged_data_total['total_damage'], color='blue', label='Total Damage', linewidth=2)

    plt.xlabel('Year')
    plt.ylabel('GDP and Total Damage')
    plt.title('Total Correlation of GDP and Total Damage Over All Years')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.show()

def load_bea_gdp_data2(db_path):
    conn = sqlite3.connect(db_path)

    query = """
    SELECT
        UPPER(GeoNames.GeoName) AS State,
        GDPData.Year,
        GDPData.Value AS GDP,
        Indicators.Description AS Indicator,
        Indicators.IndicatorID AS IndicatorIDs
    FROM GDPData
    JOIN GeoNames ON GDPData.GeoNameID = GeoNames.GeoNameID
    JOIN Indicators ON GDPData.IndicatorID = Indicators.IndicatorID
    WHERE GDPData.IndicatorID IN (2, 3, 4)
    """

    gdp_data = pd.read_sql(query, conn)

    conn.close()
    return gdp_data

def calculate_correlation_total(storm_data, gdp_data, indicator_id):
    total_damage = storm_data.groupby('YEAR')['total_damage'].sum().reset_index()

    gdp_data_filtered = gdp_data[gdp_data['IndicatorIDs'] == indicator_id]

    total_gdp = gdp_data_filtered.groupby('Year')['GDP'].sum().reset_index()

    merged_data = pd.merge(total_damage, total_gdp, left_on="YEAR", right_on="Year")

    correlation = merged_data[['total_damage', 'GDP']].corr().iloc[0, 1]

    print(f"Correlation between total damage and the specified indicator (ID {indicator_id}): {correlation}")

def correlation_real_per_capita_income(storm_data, gdp_data):
    print("\nCorrelation between Real per capita personal income and total damage:")
    calculate_correlation_total(storm_data, gdp_data, indicator_id=3)

def correlation_real_pce(storm_data, gdp_data):
    print("\nCorrelation between Real PCE and total damage:")
    calculate_correlation_total(storm_data, gdp_data, indicator_id=4)
def main():
    storm_db_path = "../data/storm_gdb_analysis.db"
    bea_db_path = "../data/gdp_data.db"

    storm_data = load_storm_events_data(storm_db_path)

    gdp_data = load_bea_gdp_data(bea_db_path)

    correlations_gdp = calculate_correlations(storm_data, gdp_data)

    negative_state_gdp, positive_state_gdp = get_extreme_correlation_states(correlations_gdp)
    print_total_correlation_for_extreme_states(storm_data, gdp_data, negative_state_gdp, positive_state_gdp)

    merged_data_total = calculate_total_correlation(storm_data, gdp_data)
    plot_total_correlation(merged_data_total)

    plot_extreme_states(storm_data, gdp_data, negative_state_gdp, positive_state_gdp)

    gdp_data2 = load_bea_gdp_data2(bea_db_path)

    correlation_real_per_capita_income(storm_data, gdp_data2)
    correlation_real_pce(storm_data, gdp_data2)

if __name__ == "__main__":
    main()
