import pandas as pd
import matplotlib.pyplot as plt
import requests
from io import StringIO
from matplotlib.animation import FuncAnimation
import seaborn as sns

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

        # Try loading the CSV with different delimiters and column setups
        try:
            df = pd.read_csv(csv_data, sep=';', usecols=[0, 2], names=["Name", "Occurrences"], skiprows=1)
        except pd.errors.ParserError:
            csv_data.seek(0)  # Reset the StringIO object to read again
            df = pd.read_csv(csv_data, sep=',', usecols=[0, 2], names=["Name", "Occurrences"], skiprows=1)

        # Ensure Occurrences is cleaned and converted to an integer
        df['Occurrences'] = df['Occurrences'].astype(str).str.replace(' ', '').astype(int)
        
        # Return the top 10 names
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

# Assign unique colors to each name
palette = sns.color_palette("hsv", len(all_names))
color_map = dict(zip(sorted(all_names), palette))

# Function to update the bar chart for each frame
def update(year):
    plt.cla()  # Clear the current axes
    data = name_trends.loc[year].sort_values(ascending=False).head(10)
    colors = [color_map[name] for name in data.index]  # Get colors based on names
    plt.barh(data.index, data.values, color=colors)
    plt.xlabel('Occurrences')
    plt.ylabel('Names')
    plt.title(f'Top 10 Most Popular Male Names in Poland - {year}')
    plt.xlim(0, name_trends.max().max() * 1.1)
    plt.gca().invert_yaxis()  # To display the highest value at the top

# Create the figure and run the animation
fig = plt.figure(figsize=(10, 6))
anim = FuncAnimation(fig, update, frames=sorted(urls.keys()), repeat=False, interval=2000)

plt.show()
