import pandas as pd
import matplotlib.pyplot as plt
import requests
from io import StringIO
from matplotlib.animation import FuncAnimation
import seaborn as sns

# URLs for male names (2019-2023)
male_urls = {
    2023: "https://api.dane.gov.pl/resources/54099,imiona-meskie-nadane-dzieciom-w-polsce-w-2023-r-imie-pierwsze/csv",
    2022: "https://api.dane.gov.pl/resources/44825,imiona-meskie-nadane-dzieciom-w-polsce-w-2022-r-imie-pierwsze/csv",
    2021: "https://api.dane.gov.pl/resources/36393,imiona-meskie-nadane-dzieciom-w-polsce-w-2021-r-imie-pierwsze/csv",
    2020: "https://api.dane.gov.pl/resources/28020,imiona-meskie-nadane-dzieciom-w-polsce-w-2020-r-imie-pierwsze/csv",
    2019: "https://api.dane.gov.pl/resources/21454,imiona-meskie-nadane-dzieciom-w-polsce-w-2019-r-imie-pierwsze/csv"
}

# URLs for female names (2019-2023)
female_urls = {
    2023: "https://api.dane.gov.pl/resources/54100,imiona-zenskie-nadane-dzieciom-w-polsce-w-2023-r-imie-pierwsze/csv",
    2022: "https://api.dane.gov.pl/resources/44824,imiona-zenskie-nadane-dzieciom-w-polsce-w-2022-r-imie-pierwsze/csv",
    2021: "https://api.dane.gov.pl/resources/36394,imiona-zenskie-nadane-dzieciom-w-polsce-w-2021-r-imie-pierwsze/csv",
    2020: "https://api.dane.gov.pl/resources/28021,imiona-zenskie-nadane-dzieciom-w-polsce-w-2020-r-imie-pierwsze/csv",
    2019: "https://api.dane.gov.pl/media/resources/20200129/imiona_%C5%BCe%C5%84skie_2019_imi%C4%99__pierwsze.csv"
}

# URL for data from 2000-2018 (same for both male and female)
url_2000_2018 = "https://api.dane.gov.pl/resources/21458,imiona-nadane-dzieciom-w-polsce-w-latach-2000-2019-imie-pierwsze/csv"

# Prompt the user to choose gender
gender = input("Please choose the gender for the chart ('M' for male, 'K' for female): ").strip().upper()

# Prompt the user to choose data type (percentage share or absolute values)
data_type = input("Please choose the data type ('percentage' for percentage share, 'absolute' for absolute values): ").strip().lower()

# Choose the correct URLs based on the user's input
if gender == 'M':
    urls = male_urls
    gender_label = 'M'
elif gender == 'K':
    urls = female_urls
    gender_label = 'K'
else:
    raise ValueError("Invalid input! Please enter 'M' for male or 'K' for female.")

# Function to load data from a URL and return a DataFrame with the top 10 names
def load_top_10_names(url, sep=',', usecols=[0, 2], skiprows=1, col_names=["Name", "Occurrences"]):
    response = requests.get(url)
    if response.status_code == 200:
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data, sep=sep, usecols=usecols, names=col_names, skiprows=skiprows)
        df['Occurrences'] = df['Occurrences'].astype(str).str.replace(' ', '').astype(int)
        df['Percentage'] = df['Occurrences'] / df['Occurrences'].sum() * 100
        return df.nlargest(10, 'Occurrences')
    else:
        print(f"Failed to retrieve data for URL: {url}")
        return pd.DataFrame()

# Load data for each year and store in a dictionary
top_names = {}

# Load data from 2019-2023
for year, url in urls.items():
    top_names[year] = load_top_10_names(url)

# Load and process data from 2000-2018, filtering by the chosen gender
response = requests.get(url_2000_2018)
if response.status_code == 200:
    csv_data = StringIO(response.text)
    df_2000_2018 = pd.read_csv(csv_data, sep=',', usecols=[0, 1, 2, 3], names=["Year", "Name", "Occurrences", "Gender"], skiprows=1)
    
    # Filter for the chosen gender
    df_2000_2018 = df_2000_2018[df_2000_2018['Gender'] == gender_label]
    
    df_2000_2018['Occurrences'] = df_2000_2018['Occurrences'].astype(str).str.replace(' ', '').astype(int)
    df_2000_2018['Percentage'] = df_2000_2018['Occurrences'] / df_2000_2018.groupby('Year')['Occurrences'].transform('sum') * 100
    
    # Get top 10 names for each year and add them to the dictionary
    for year in df_2000_2018['Year'].unique():
        df_year = df_2000_2018[df_2000_2018['Year'] == year]
        top_names[int(year)] = df_year.nlargest(10, 'Occurrences')
else:
    print(f"Failed to retrieve data for URL: {url_2000_2018}")

# Extract all unique names from the top 10 of each year
all_names = set()
for df in top_names.values():
    all_names.update(df['Name'])

# Create a DataFrame to hold occurrences or percentages for each name across years
if data_type == 'percentage':
    name_trends = pd.DataFrame(index=sorted(top_names.keys()), columns=sorted(all_names)).fillna(0)
    value_column = 'Percentage'
else:
    name_trends = pd.DataFrame(index=sorted(top_names.keys()), columns=sorted(all_names)).fillna(0)
    value_column = 'Occurrences'

# Populate the DataFrame with occurrences or percentages
for year, df in top_names.items():
    for _, row in df.iterrows():
        name_trends.at[year, row['Name']] = row[value_column]

# Assign unique colors to each name
palette = sns.color_palette("hsv", len(all_names))
color_map = dict(zip(sorted(all_names), palette))

# Function to update the bar chart for each frame
def update(year):
    plt.cla()  # Clear the current axes
    data = name_trends.loc[year].sort_values(ascending=False).head(10)
    colors = [color_map[name] for name in data.index]  # Get colors based on names
    plt.barh(data.index, data.values, color=colors)
    plt.xlabel('Percentage (%)' if data_type == 'percentage' else 'Occurrences')
    plt.ylabel('Names')
    plt.title(f'Top 10 Most Popular {("Male" if gender == "M" else "Female")} Names in Poland - {year} ({data_type.capitalize()})')
    plt.xlim(0, name_trends.max().max() * 1.1)
    plt.gca().invert_yaxis()  # To display the highest value at the top

# Create the figure and run the animation
fig = plt.figure(figsize=(10, 6))
anim = FuncAnimation(fig, update, frames=sorted(top_names.keys()), repeat=False, interval=2000)

plt.show()