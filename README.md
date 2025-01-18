# Impact of Extreme Weather Events on the USA

## Project Description

The trend of extreme weather phenomena that include storms, floods and tornadoes has intensified in many regions within the United States. This is a trend of events that brings forth
questions about their economic implications. The central question that this report is about to
address is:

### To what extent do extreme weather events such as storms, floods and tornadoes impact the GDP of the United States and consequently the availability of financial resources?

The study addresses this issue by analyzing historical data on weather patterns and key economic
indicators, focusing on regions most vulnerable to substantial losses. By estimating the economic
damages caused by these events, the analysis hopes to provide actionable insights for policymakers
and stakeholders, fostering better preparedness and enhancing economic resilience against future
disasters.

The project work is divided into 4 steps:

1. **Data Collection**: Gathering relevant data from the NOAA Storm Events Database and BEA.
2. **Data Analysis**: Initial analysis of the data to identify trends and patterns.
3. **Data Transformation**: Transforming raw data into a format suitable for analysis.
4. **Data Interpretation/Correlation**: Interpreting the results and examining the correlations between extreme weather events and economic factors.

## Data Sources

- **NOAA Storm Events Database**: Contains information on extreme weather events in the U.S.
- **Bureau of Economic Analysis (BEA) - GDP by State**: Contains data on the GDP of individual U.S. states and the U.S. overall.

## Project Goals

- **Understanding potential Correlations**: Investigating correlations between extreme weather events and economic factors like real personal income and real PCE.
- **Economic Impacts**: Determining the economic impact of extreme weather events on different states in the U.S.

## Data Structure

- **NOAA Storm Events Database**:
  - `Event Type`: Type of extreme weather event (e.g., tornado, storm, flood).
  - `State`: Affected state.
  - `Date`: Date of the event.
  - `Damage`: Amount of damage (in dollars).

- **BEA - GDP by State**:
  - `State`: U.S. state.
  - `Year`: Year of data collection.
  - `Real GDP`: Real gross domestic product
  - `Real Personal Income`: Real personal income in millions of dollars (inflation-adjusted).
  - `Real PCE`: Real personal consumption expenditure in millions of dollars (inflation-adjusted).


## Installation

### Prerequisites

- Python 3.9 or higher
- The following Python libraries:
  - pandas
  - requests
  - beautifulsoup4
  - selenium
  - matplotlib

## Purpose of Py-Files

- pipeline.py is used for data-acquisition and -transformation into a fitting format for sql-tables
- data_correlation.py is used to calculate the overall correlation and the correlation on the state level