import requests

def get_existing_urls(database_id, headers):
    query_url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.post(query_url, headers=headers)
    if response.status_code == 200:
        pages = response.json()["results"]
        existing_urls = [page["properties"]["Link"]["url"] for page in pages if "Link" in page["properties"]]
        return existing_urls
    else:
        print(f"Failed to query database. Status code: {response.status_code}\nResponse: {response.text}")
        return []
