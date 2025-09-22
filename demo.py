#!/usr/bin/env python3
"""
Demo script for the Car Listing Agent
This shows how to use the system without requiring an API key
"""

from car_scraper import CarScraper

def demo_car_search():
    """Demonstrate the car search functionality"""
    print("🚗 Car Listing Agent - Demo")
    print("=" * 40)
    
    # Initialize the scraper
    scraper = CarScraper()
    
    # Test queries
    test_queries = [
        "Honda Civic",
        "Toyota Camry under $25000",
        "BMW X3 luxury SUV",
        "Ford F-150 pickup truck"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 30)
        
        # Parse the query
        make, model = scraper._parse_car_query(query)
        print(f"Parsed - Make: {make}, Model: {model}")
        
        # Note: Actual web scraping would require the full system
        print("✅ Query parsing successful")
        print("ℹ️  For full functionality, set up your OpenAI API key")

def main():
    """Run the demo"""
    try:
        demo_car_search()
        print("\n" + "=" * 40)
        print("🎉 Demo completed successfully!")
        print("\nTo use the full system:")
        print("1. Create a .env file with your OpenAI API key:")
        print("   OPENAI_API_KEY=your_actual_api_key_here")
        print("2. Run: python car_agent.py")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    main()


