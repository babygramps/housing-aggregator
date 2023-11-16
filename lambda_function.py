import requests
from bs4 import BeautifulSoup
import asyncio
import os

# Import helper functions

from helperFunctions.search_database import search_database
from helperFunctions.create_database import create_database
from helperFunctions.get_amenities_from_listing import  get_amenities_from_listing
from helperFunctions.get_existing_urls import get_existing_urls
from helperFunctions.amenities import amenities_list

# Initialize environmental variables

from dotenv import load_dotenv
load_dotenv()


# Notion setup

notion_token = os.environ.get("NOTION_TOKEN")
version = '2022-02-22'
headers = {
    "Authorization": f"Bearer {notion_token}",
    "Content-Type": "application/json",
    "Notion-Version": version
}
search_url = "https://api.notion.com/v1/search"
create_db_url = "https://api.notion.com/v1/databases"
create_page_url = "https://api.notion.com/v1/pages"
database_title = "Craigslist housing aggregator"

# Main scraper and update function

async def main():

    # Search Notion for the database. Create a new one if not found

    database_id = await search_database(database_title, search_url, headers)
    if not database_id:
        parent_page_id = '39e0659f0f094f15b3646f3fab3895bd'
        database_id = create_database(parent_page_id, database_title, create_db_url, headers)
        print(f'database created')
        if not database_id:
            print("Failed to create or find the database.")
            exit()

    url = 'https://sfbay.craigslist.org/search/eby/apa'
    params = {
        'housing_type': [3, 4, 5, 6, 7],
        'max_bedrooms': 2,
        'nh': [112, 46, 47, 48, 49, 60, 62, 63, 65, 66],
        'pets_dog': 1
    }

    # Get existing Craigslist post urls saved in Notion

    existing_urls = get_existing_urls(database_id, headers)

    # Start scraping

    response = requests.get(url, params=params)
    if response.status_code == 200:
        print(f'Beginning the scrape...')
        soup = BeautifulSoup(response.content, 'html.parser')
        postings = soup.find_all('li', class_='cl-static-search-result')

        # Do these tasks for each posting found in Craigslist

        for post in postings:
            try:

                # Get post attributes and format them

                title = post['title']
                link = post.a['href']
                price = post.find('div', class_='price').text.strip()
                location = post.find('div', class_='location').text.strip()

                listing_response = requests.get(link)
                if listing_response.status_code == 200:
                    listing_soup = BeautifulSoup(listing_response.content, 'html.parser')
                    size_elem = listing_soup.find('span', class_='housing').text.strip()

                # Initialize br and ft2 as 'N/A'

                br = 'N/A'
                ft2 = 'N/A'

                # Clean up the size_elem and split it into separate columns for "br" and "ft2"

                size_cleaned = size_elem.replace("/", "").strip()
                size_parts = size_cleaned.split()
                
                if size_parts:
                    for part in size_parts:
                        if part.endswith('br'):
                            br = part
                        elif part.endswith('ft2'):
                            ft2 = part

                    # Get listing text from Craigslist post

                    listing_text = listing_soup.get_text()
                    
                    if link not in existing_urls:
                        listing_response = requests.get(link)
                        if listing_response.status_code == 200:
                            listing_soup = BeautifulSoup(listing_response.content, 'html.parser')
                            listing_text = listing_soup.get_text()

                            # Use OpenAI API to find amenities in Craiglist link

                            amenities_summary = await get_amenities_from_listing(listing_text)
                            found_amenities = [amenity for amenity in amenities_list if amenity in amenities_summary]

                            # Checking if the date is available and valid, else using a default date
                            date_elem = listing_soup.find('time', class_='date timeago')['datetime']
                            valid_date = date_elem.split("T")[0] if date_elem else '2023-01-01'  # Using a default date
                         
                            # Create payload to save record in Notion

                            notion_payload = {
                                "parent": {"database_id": database_id},
                                "properties": {
                                    "Title": {"title": [{"text": {"content": title}}]},
                                    "Price": {"number": int(price.replace("$", "").replace(",", "")) if price.startswith("$") else 0},
                                    "Location": {"select": {"name": location}},
                                    "Bedroom": {"select": {"name": br}},  # Update as needed
                                    "Sq ft": {"rich_text": [{"text": {"content": ft2}}]},  # Update as needed
                                    "Date": {"date": {"start": valid_date}},  # Update as needed
                                    "Link": {"url": link},
                                    "Amenities": {"multi_select": [{"name": amenity} for amenity in found_amenities]}
                                }
                            }
                            response = requests.post(create_page_url, headers=headers, json=notion_payload)
                            if response.status_code != 200:
                                print(f"Failed to add listing to Notion database. Status code: {response.status_code}\nResponse: {response.text}")
                            elif response.status_code == 200:
                                print(f'{link} saved successfully!')
                        else:
                            print(f"URL already exists in database: {link}")
                    else:
                        print(f'{link} has already been logged')
            except AttributeError:
                continue
    else:
        print(f"Failed to retrieve data: {response.status_code}")
    print(f'Function complete')

if __name__ == "__main__":
    asyncio.run(main())
