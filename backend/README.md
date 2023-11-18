# Craigslist Housing Aggregator

## Overview
The Craigslist Housing Aggregator is an automated tool designed to scrape housing listings from Craigslist, summarize their amenities using OpenAI's GPT-3, and store this data in a Notion database. 

## Features
- **Scrapes Craigslist**: Automatically gathers housing listings from Craigslist.
- **Amenities Analysis**: Utilizes OpenAI's GPT-3 to extract and summarize key amenities from each listing.
- **Notion Integration**: Seamlessly stores and organizes listing data in a Notion database.

## Technologies Used
- Python: For backend scripting.
- BeautifulSoup: To scrape website data.
- OpenAI's GPT-3: For natural language processing.
- AWS Lambda with Docker: For deployment and automation.
- AWS EventBridge: To schedule daily scraping tasks.

## Security
- Environment Variables: Used to securely manage API keys and tokens.

This tool streamlines the process of gathering and analyzing housing listings, making it an invaluable resource for housing market analysis or personal use.
