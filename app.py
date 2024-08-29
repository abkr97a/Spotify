import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load and preprocess data
df = pd.read_csv('/content/universal_top_spotify_songs.csv')
df = df.dropna(subset=['country', 'artists', 'name', 'album_name', 'album_release_date'])
df['snapshot_date'] = pd.to_datetime(df['snapshot_date'])
df['album_release_date'] = pd.to_datetime(df['album_release_date'])
df['since_release'] = (df['snapshot_date'] - df['album_release_date']).dt.days
df['is_explicit'] = df['is_explicit'].astype('category')
df['release_year'] = df['album_release_date'].dt.year
df['release_month'] = df['album_release_date'].dt.month
df['release_day'] = df['album_release_date'].dt.day
df['snapshot_year'] = df['snapshot_date'].dt.year
df['snapshot_month'] = df['snapshot_date'].dt.month
df['snapshot_day'] = df['snapshot_date'].dt.day
iso = pd.read_excel('/content/country codes.xls')
df = pd.merge(df, iso[['Code Value', 'Definition']], left_on='country', right_on='Code Value', how='left')
df.rename(columns={'country': 'country_code', 'Definition': 'country_name'}, inplace=True)
df = df.drop('Code Value', axis=1)

# Streamlit app
st.title('Spotify Analysis Dashboard')

# Section 1: Country Selection
st.header("Country Filter")
selected_country = st.selectbox('Select a country:', df['country_name'].unique())

# Section 2: Date Range Filter
st.header("Date Range Filter")
min_date = df['snapshot_date'].min().date()
max_date = df['snapshot_date'].max().date()

date_range = st.slider('Select the time period for analysis:',
                       min_value=min_date,
                       max_value=max_date,
                       value=(min_date, max_date))

# Filter the data by the selected country and date range
df_filtered = df[(df['country_name'] == selected_country) &
                 (df['snapshot_date'].dt.date >= date_range[0]) &
                 (df['snapshot_date'].dt.date <= date_range[1])]

# Section 3: Average Reading for Features
st.header(f"Average Reading for Features in {selected_country} (Filtered by Date Range)")
features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 
            'instrumentalness', 'liveness', 'valence']

# Calculate the average values for the selected country and date range
average_values = df_filtered[features].mean().reset_index()
average_values.columns = ['Feature', 'Average Value']

# Plotting the average values
plt.figure(figsize=(10, 6))
plt.bar(average_values['Feature'], average_values['Average Value'], color='skyblue')
plt.title(f'Average Values for Different Features in {selected_country}')
plt.xlabel('Feature')
plt.ylabel('Average Value')
plt.xticks(rotation=45)
st.pyplot(plt)

# Section 4: Top 10 Songs by Popularity
st.header(f"Top 10 Songs by Popularity in {selected_country} (Filtered by Date Range)")

# Aggregate the popularity for each song and get the top 10
top_songs = df_filtered.groupby('name')['popularity'].mean().reset_index()
top_songs = top_songs.sort_values(by='popularity', ascending=False).head(10)

st.write(top_songs)

# Section 5: Top 10 Artists
st.header(f"Top 10 Artists in {selected_country} (Filtered by Date Range)")

# Aggregate the popularity for each artist and get the top 10
top_artists = df_filtered.groupby('artists')['popularity'].sum().reset_index()
top_artists = top_artists.sort_values(by='popularity', ascending=False).head(10)

st.write(top_artists)

# Summary
st.header("Summary and Insights")
st.write(f"The dashboard provides insights into the music trends in {selected_country} over the selected date range, showing the average values for different features, the top 10 most popular songs, and the top 10 most popular artists.")
