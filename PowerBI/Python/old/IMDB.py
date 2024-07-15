import requests
from selectolax.parser import HTMLParser
import chompjs
import pandas as pd

url = 'https://www.imdb.com/chart/top/'

# Defining the User-Agent header to use in the GET request below
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}

# Retrieving the target web page
page = requests.get(url, headers=headers)

# Parsing the target web page
html = HTMLParser(page.text)
data = html.css("script[type='application/json']")

new = None
for script in data:
    try:
        new = chompjs.parse_js_object(script.text())
        break
    except chompjs.ChompjsException as e:
        print(f"Error parsing script: {e}")

# List to hold the data
data_list = []

if new is None:
    print("No valid JSON data found.")
else:
    for i in range(250):
        try:
            node = new['props']['pageProps']['pageData']['chartTitles']['edges'][i]['node']
            id = node['id']
            rank = new['props']['pageProps']['pageData']['chartTitles']['edges'][i]['currentRank']
            rus_title = node['titleText']['text']
            orig_title = node['originalTitleText']['text']
            year = node['releaseYear']['year']
            rating = node['ratingsSummary']['aggregateRating']
            rating_count = node['ratingsSummary']['voteCount']
            runtime = node['runtime']['seconds']

            # Extracting certificate rating with debug information
            certificate = node.get('certificate', {})
            if isinstance(certificate, dict):
                age = certificate.get('rating', 'N/A')
            else:
                print(f"Unexpected certificate structure at index {i}: {certificate}")
                age = 'N/A'

            genres_list = [genre['genre']['text'] for genre in node['titleGenres']['genres']]

            # Append data to list
            data_list.append({
                'Rank': rank,
                'ID': id,
                'Russian Title': rus_title,
                'Original Title': orig_title,
                'Year': year,
                'Rating': rating,
                'Rating Count': rating_count,
                'Runtime (sec)': runtime,
                'Age': age,
                'Genres': ', '.join(genres_list),
            })
        except KeyError as e:
            print(f"Missing data for index {i}: {e}")
        except Exception as e:
            print(f"An error occurred at index {i}: {e}")

# Create DataFrame and save to Excel
df = pd.DataFrame(data_list)
df.to_excel('imdb_top_250.xlsx', index=False)

print("Data successfully written to 'imdb_top_250.xlsx'")