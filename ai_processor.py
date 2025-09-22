import openai
from typing import List, Dict
from config import Config

class AIProcessor:
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
        
        openai.api_key = Config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def process_query(self, user_query: str) -> str:
        """Process user query to extract car search parameters"""
        try:
            prompt = f"""
            Analyze this car search query and extract the key information in a structured format:
            Query: "{user_query}"
            
            Extract:
            1. Car make/brand (e.g., Toyota, Honda, BMW)
            2. Car model (e.g., Camry, Accord, X3)
            3. Year range (e.g., 2020-2023, 2019 or newer)
            4. Price range (e.g., under $25000, $15000-$30000)
            5. Any specific features (e.g., automatic transmission, AWD, hybrid)
            6. Mileage preferences (e.g., low mileage, under 50000 miles)
            
            Format your response as:
            Make: [extracted make or "any"]
            Model: [extracted model or "any"]
            Year: [year range or "any"]
            Price: [price range or "any"]
            Features: [specific features or "none"]
            Mileage: [mileage preferences or "any"]
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a car search assistant that extracts structured information from user queries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error processing query with AI: {e}")
            return f"Make: any\nModel: any\nYear: any\nPrice: any\nFeatures: none\nMileage: any"
    
    def enhance_search_query(self, user_query: str) -> str:
        """Enhance the user query for better web scraping"""
        try:
            prompt = f"""
            Convert this car search request into a clear, search-optimized query for car listing websites:
            Original query: "{user_query}"
            
            Create a concise search query that includes:
            - Car make and model
            - Key specifications or features
            - Any specific requirements
            
            Keep it under 10 words and use common car terminology.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a car search optimization assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error enhancing search query: {e}")
            return user_query
    
    def analyze_listings(self, listings: List[Dict], user_query: str) -> str:
        """Analyze car listings and provide insights"""
        if not listings:
            return "No car listings found for your search criteria."
        
        try:
            # Prepare listings data for analysis
            listings_text = ""
            for i, listing in enumerate(listings[:5], 1):  # Analyze top 5
                listings_text += f"{i}. {listing['title']} - {listing['price']} - {listing['mileage']}\n"
            
            prompt = f"""
            Analyze these car listings and provide insights based on the user's original query:
            
            User Query: "{user_query}"
            
            Available Listings:
            {listings_text}
            
            Provide:
            1. Summary of what was found
            2. Price range analysis
            3. Best value recommendations
            4. Any important considerations or warnings
            5. Suggestions for refining the search if needed
            
            Keep response concise but informative.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a car buying expert that analyzes listings and provides helpful insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.2
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error analyzing listings: {e}")
            return "Found listings but unable to provide detailed analysis."


