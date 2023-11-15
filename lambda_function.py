import requests
from bs4 import BeautifulSoup
from openai import AsyncOpenAI
import asyncio
import os

# OpenAI setup
client = AsyncOpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=os.environ.get("OPENAI_KEY"),
)
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

# Search for existing Notion database
def search_database(title):
    search_payload = {
        "query": title,
        "filter": {
            "value": "database",
            "property": "object"
        }
    }
    response = requests.post(search_url, headers=headers, json=search_payload)
    if response.status_code == 200:
        databases = response.json()["results"]
        for db in databases:
            if db["title"][0]["text"]["content"] == title:
                return db["id"]
    return None

# Create a notion database if one doesn't exist with the appropriate schema

def create_database(parent_page_id):
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": database_title}}],
        "properties": {
            "Title": {"title": {}},
            "Price": {"number": {"format": "dollar"}},
            "Location": {"select": {}},
            "Bedroom": {"select": {}},
            "Sq ft": {"rich_text": {}},
            "Date": {"date": {}},
            "Link": {"url": {}},
            "Amenities": {"multi_select": {}}
        }
    }
    response = requests.post(create_db_url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["id"]
    else:
        return None
    
# Use OpenAI API to generate a list of amenities from Craiglist post

async def get_amenities_from_listing(listing_text):
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role":"user",
            "content":f"Summarize the following listing then check if the following amenities are included in the listing: Air Conditioning, Heating System, Laundry Facilities, Dishwasher, Refrigerator, Stove/Oven, Microwave, Garbage Disposal, Internet Access, Cable-Ready Outlets, Balcony/Patio, Storage Space, Covered Parking, Garage, Pool, Fitness Center, Clubhouse, Playground, Pet-Friendly Options, Security System, On-site Management, Elevator, Public Transportation Access, Smoke-Free Environment, Wheelchair Access. If you see a match, return the matching amenity. Do not add any other words, just a list of the matching amentities. Format the list exactly like this: Matching amentities: amentity 1, amenity 2, etc:\n\n{listing_text}"
        }]
    )
    return response.choices[0].message.content

def get_existing_urls(database_id):
    query_url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.post(query_url, headers=headers)
    if response.status_code == 200:
        pages = response.json()["results"]
        existing_urls = [page["properties"]["Link"]["url"] for page in pages if "Link" in page["properties"]]
        return existing_urls
    else:
        print(f"Failed to query database. Status code: {response.status_code}\nResponse: {response.text}")
        return []


async def main():
    database_id = search_database(database_title)
    if not database_id:
        parent_page_id = '39e0659f0f094f15b3646f3fab3895bd'
        database_id = create_database(parent_page_id)
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

    existing_urls = get_existing_urls(database_id)

    response = requests.get(url, params=params)
    if response.status_code == 200:
        print(f'Beginning the scrape...')
        soup = BeautifulSoup(response.content, 'html.parser')
        postings = soup.find_all('li', class_='cl-static-search-result')

        for post in postings:
            try:
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
                    listing_text = listing_soup.get_text()
                    if link not in existing_urls:
                        listing_response = requests.get(link)
                        if listing_response.status_code == 200:
                            listing_soup = BeautifulSoup(listing_response.content, 'html.parser')
                            listing_text = listing_soup.get_text()
                            amenities_summary = await get_amenities_from_listing(listing_text)
                            amenities_list = ["Air Conditioning",
                                                "Heating System",
                                                "Laundry Facilities",
                                                "Dishwasher",
                                                "Refrigerator",
                                                "Stove/Oven",
                                                "Microwave",
                                                "Garbage Disposal",
                                                "Internet Access",
                                                "Cable-Ready Outlets",
                                                "Balcony/Patio",
                                                "Storage Space",
                                                "Covered Parking",
                                                "Garage",
                                                "Pool",
                                                "Fitness Center",
                                                "Clubhouse",
                                                "Playground",
                                                "Pet-Friendly Options",
                                                "Security System",
                                                "On-site Management",
                                                "Elevator",
                                                "Public Transportation Access",
                                                "Smoke-Free Environment",
                                                "Wheelchair Access"]  # List all amenities
                            found_amenities = [amenity for amenity in amenities_list if amenity in amenities_summary]

                            # Checking if the date is available and valid, else using a default date
                            date_elem = listing_soup.find('time', class_='date timeago')['datetime']
                            valid_date = date_elem.split("T")[0] if date_elem else '2023-01-01'  # Using a default date

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
                                print(f'Status code is 200')
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
