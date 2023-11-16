from openai import AsyncOpenAI
import os

from dotenv import load_dotenv
load_dotenv()


# OpenAI setup
client = AsyncOpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=os.environ.get("OPENAI_KEY")
)

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