# Project Plan

## Title
<!-- Give your project a short title. -->
Impact of Extreme Weather Events on the USA

## Main Question

<!-- Think about one main question you want to answer based on the data. -->
1. What economic impact do weather extremes such as storms, floods and tornadoes have on the USA?

## Description

<!-- Describe your data science project in max. 200 words. Consider writing about why and how you attempt it. -->
Hurricanes, floods and Tornadoes in the United States are increasing in frequency and intensity. The present study explores how the various weather extremes contribute towards regional economies by means of an in-depth analysis of economic indicators including regional gross domestic product, insurance outlay, and losses at different states. It would outline the areas that are more prone to severe economic loss because of weather. It would also give further details on how natural calamities affect economic stability. Its findings might be useful to decision-makers in developing measures and methods for risk reduction to stabilize the economy.



## Datasources

<!-- Describe each datasources you plan to use in a section. Use the prefic "DatasourceX" where X is the id of the datasource. -->

### Datasource1: NOAA Storm Events Database
* Metadata URL: https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.ncdc:C00510/html
* Metadata-URL (XML): https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.ncdc:C00510/xml
* Data URL: https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/
* Data Type: CSV
* License Type: Open Data - Citation necessary

NOAA Storm Events is a database of extreme weather events in the United States including storms, floods and Tornadoes with locations, dates, and impact notes of the events. It is ideal for analyzing how often and in what regions extreme weather events take place, and what kind of damage they cause.

### Datasource2: Bureau of Economic Analysis (BEA) - GDP by State
* Metadata URL: https://apps.bea.gov/itable/?ReqID=70&step=1#eyJhcHBpZCI6NzAsInN0ZXBzIjpbMSwyOSwyNSwzMSwyNiwyNywzMF0sImRhdGEiOltbIlRhYmxlSWQiLCI2MDAiXSxbIk1ham9yX0FyZWEiLCIwIl0sWyJTdGF0ZSIsWyIwIl1dLFsiQXJlYSIsWyJYWCJdXSxbIlN0YXRpc3RpYyIsWyItMSJdXSxbIlVuaXRfb2ZfbWVhc3VyZSIsIlBlcmNlbnRDaGFuZ2UiXSxbIlllYXIiLFsiLTEiXV0sWyJZZWFyQmVnaW4iLCItMSJdLFsiWWVhcl9FbmQiLCItMSJdXX0=
* Data URL: https://apps.bea.gov/itable/?ReqID=70&step=1#eyJhcHBpZCI6NzAsInN0ZXBzIjpbMSwyOSwyNSwzMSwyNiwyNywzMF0sImRhdGEiOltbIlRhYmxlSWQiLCI2MDAiXSxbIk1ham9yX0FyZWEiLCIwIl0sWyJTdGF0ZSIsWyIwIl1dLFsiQXJlYSIsWyJYWCJdXSxbIlN0YXRpc3RpYyIsWyItMSJdXSxbIlVuaXRfb2ZfbWVhc3VyZSIsIlBlcmNlbnRDaGFuZ2UiXSxbIlllYXIiLFsiLTEiXV0sWyJZZWFyQmVnaW4iLCItMSJdLFsiWWVhcl9FbmQiLCItMSJdXX0=
* Data Type: ZIP
* License Type: Open Data - Citation necessary (https://www.bea.gov/open-data)

BEA prepares regional statistics of economic output, including gross domestic product at the state level in the United States. These could be useful data for accounting in an economic damage study of specific weather events by state and, more generally, to study the impacts of such disasters on productivity losses and long-term economic stability.


## Work Packages

<!-- List of work packages ordered sequentially, each pointing to an issue with more details. -->

1. Data Extraction [#1][i1]
2. Data Analysis [#2] [i2]

[i1]: https://github.com/JDizzle977/made-template/issues/1
[i2]: https://github.com/JDizzle977/made-template/issues/2