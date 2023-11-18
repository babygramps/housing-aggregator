import requests

async def search_database(title, search_url, headers):
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