import requests

def create_database(parent_page_id, database_title, create_db_url, headers):
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
    