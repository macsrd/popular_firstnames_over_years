import pandas as pd
import matplotlib.pyplot as plt
import requests
from io import StringIO

# Define the years and their corresponding URLs
urls = {
    2023: "https://api.dane.gov.pl/resources/54099,imiona-meskie-nadane-dzieciom-w-polsce-w-2023-r-imie-pierwsze/csv",
    2022: "https://api.dane.gov.pl/resources/44825,imiona-meskie-nadane-dzieciom-w-polsce-w-2022-r-imie-pierwsze/csv",
    2021: "https://api.dane.gov.pl/resources/36393,imiona-meskie-nadane-dzieciom-w-polsce-w-2021-r-imie-pierwsze/csv",
    2020: "https://api.dane.gov.pl/resources/28020,imiona-meskie-nadane-dzieciom-w-polsce-w-2020-r-imie-pierwsze/csv",
    2019: "https://api.dane.gov.pl/resources/21454,imiona-meskie-nadane-dzieciom-w-polsce-w-2019-r-imie-pierwsze/csv"
}

# Function to load data from a URL and return a DataFrame with the top 10 names
def load_top_10_names(url):
    response = requests.get(url)
    if response.status_code == 200:
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data, sep=',', usecols=[0, 2], names=["Name", "Occurrences"], skiprows=1)
        #df['Occurrences'] = df['Occurrences'].str.replace(' ', '').astype(int)  # Clean and convert the occurrences to int
        top_10_df = df.nlargest(10, 'Occurrences')
        return top_10_df
    else:
        print(f"Failed to retrieve data for URL: {url}")
        return pd.DataFrame()

# Load data for each year and store in a dictionary
top_names = {}
for year, url in urls.items():
    top_names[year] = load_top_10_names(url)

# Extract all unique names from the top 10 of each year
all_names = set()
for df in top_names.values():
    all_names.update(df['Name'])

# Create a DataFrame to hold occurrences for each name across years
name_trends = pd.DataFrame(index=sorted(urls.keys()), columns=sorted(all_names)).fillna(0)

# Populate the DataFrame with occurrences
for year, df in top_names.items():
    for _, row in df.iterrows():
        name_trends.at[year, row['Name']] = row['Occurrences']

# Plot the data
plt.figure(figsize=(14, 8))
for name in name_trends.columns:
    plt.plot(name_trends.index, name_trends[name], marker='o', label=name)

plt.title('Top 10 Most Popular Male Names in Poland (2019-2023)')
plt.xlabel('Year')
plt.ylabel('Occurrences')
plt.xticks(sorted(urls.keys()))
plt.legend(title="Names", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
