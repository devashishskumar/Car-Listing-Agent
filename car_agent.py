#!/usr/bin/env python3
"""
Car Listing Viewing Agent
A simple agent that searches for car listings based on user queries using web scraping and AI analysis.
"""

import os
import sys
from typing import List, Dict
from car_scraper import CarScraper
from ai_processor import AIProcessor
from config import Config

class CarAgent:
    def __init__(self):
        try:
            self.scraper = CarScraper()
            self.ai_processor = AIProcessor()
            print("🚗 Car Listing Agent initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing Car Agent: {e}")
            print("Please make sure your OpenAI API key is set in the .env file")
            sys.exit(1)
    
    def process_user_query(self, query: str) -> None:
        """Main method to process user queries and return car listings"""
        print(f"\n🔍 Searching for: '{query}'")
        print("⏳ Please wait while I search for car listings...")
        
        try:
            # Step 1: Enhance the search query using AI
            enhanced_query = self.ai_processor.enhance_search_query(query)
            print(f"📝 Enhanced search query: '{enhanced_query}'")
            
            # Step 2: Scrape car listings from websites
            listings = self.scraper.search_all_sites(enhanced_query)
            
            if not listings:
                print("❌ No car listings found. Try adjusting your search criteria.")
                return
            
            # Step 3: Display listings
            self.display_listings(listings)
            
            # Step 4: Provide AI analysis
            print("\n🤖 AI Analysis:")
            print("-" * 50)
            analysis = self.ai_processor.analyze_listings(listings, query)
            print(analysis)
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
    
    def display_listings(self, listings: List[Dict]) -> None:
        """Display car listings in a formatted way"""
        print(f"\n📋 Found {len(listings)} car listings:")
        print("=" * 80)
        
        for i, listing in enumerate(listings, 1):
            print(f"\n{i}. {listing['title']}")
            print(f"   💰 Price: {listing['price']}")
            print(f"   🛣️  Mileage: {listing['mileage']}")
            print(f"   📍 Location: {listing['location']}")
            print(f"   🌐 Source: {listing['source']}")
            if listing.get('url') and listing['url'] != 'N/A':
                print(f"   🔗 URL: {listing['url']}")
            print("-" * 40)
    
    def run_interactive_mode(self) -> None:
        """Run the agent in interactive chat mode"""
        print("\n" + "="*60)
        print("🚗 WELCOME TO CAR LISTING AGENT 🚗")
        print("="*60)
        print("I can help you find car listings based on your requirements!")
        print("Examples of queries you can try:")
        print("• 'Find me a Honda Civic under $20,000'")
        print("• 'Looking for a BMW X3 with low mileage'")
        print("• 'Toyota Camry 2020 or newer'")
        print("• 'Electric car under $30,000'")
        print("\nType 'quit' or 'exit' to stop the agent.")
        print("-" * 60)
        
        while True:
            try:
                query = input("\n🔍 What kind of car are you looking for? ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thank you for using Car Listing Agent! Goodbye!")
                    break
                
                if not query:
                    print("❌ Please enter a search query.")
                    continue
                
                self.process_user_query(query)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")

def main():
    """Main function to run the Car Agent"""
    # Check if API key is available
    if not Config.OPENAI_API_KEY:
        print("❌ OpenAI API key not found!")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return
    
    # Initialize and run the agent
    agent = CarAgent()
    
    # Check if query provided as command line argument
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        agent.process_user_query(query)
    else:
        # Run in interactive mode
        agent.run_interactive_mode()

if __name__ == "__main__":
    main()

