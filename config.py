import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Car listing websites to search
    CAR_WEBSITES = {
        'cars.com': 'https://www.cars.com/shopping/results/?zip=75001&maximum_distance=50&makes[]=',
        'autotrader.com': 'https://www.autotrader.com/cars-for-sale/all-cars',
        'cargurus.com': 'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action'
    }
    
    # Headers for web scraping
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }



