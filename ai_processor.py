import openai
from typing import List, Dict
from config import Config
from conversation_manager import ConversationManager

class AIProcessor:
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
        
        openai.api_key = Config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.conversation_manager = ConversationManager()
    
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
    
    def process_conversational_message(self, user_message: str, user_id: str = "default") -> Dict:
        """Process a conversational message and determine the response"""
        try:
            # Add user message to conversation
            self.conversation_manager.add_message(user_id, "user", user_message)
            
            # Get conversation history for context
            conversation_history = self.conversation_manager.get_conversation_history(user_id)
            
            # Check if user wants to search for cars
            should_search = self.conversation_manager.should_search_for_cars(user_message, conversation_history)
            
            if should_search:
                # Extract criteria and generate search query
                criteria = self.conversation_manager.extract_car_criteria(user_message)
                search_query = self.conversation_manager.generate_search_query(criteria)
                
                # Generate conversational response
                response = self._generate_conversational_response(user_message, conversation_history, should_search=True)
                
                return {
                    "type": "search_request",
                    "response": response,
                    "search_query": search_query,
                    "criteria": criteria
                }
            else:
                # Generate conversational response without search
                response = self._generate_conversational_response(user_message, conversation_history, should_search=False)
                
                return {
                    "type": "conversation",
                    "response": response,
                    "search_query": None,
                    "criteria": None
                }
                
        except Exception as e:
            print(f"Error in conversational processing: {e}")
            return {
                "type": "error",
                "response": "I'm sorry, I encountered an error. Could you please try again?",
                "search_query": None,
                "criteria": None
            }
    
    def _generate_conversational_response(self, user_message: str, conversation_history: List[Dict], should_search: bool = False) -> str:
        """Generate a conversational response using OpenAI"""
        try:
            # Prepare conversation context
            messages = conversation_history[-10:]  # Last 10 messages for context
            
            if should_search:
                system_message = """You are a helpful car buying assistant. The user has indicated they want to search for cars. 
                Be encouraging and let them know you're searching for their ideal car. Keep your response brief and friendly."""
            else:
                system_message = """You are a helpful car buying assistant. The user is having a conversation with you. 
                Be friendly, helpful, and guide them toward telling you what kind of car they're looking for. 
                Ask clarifying questions if needed."""
            
            # Add system message if not already present
            if not messages or messages[0]["role"] != "system":
                messages.insert(0, {"role": "system", "content": system_message})
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating conversational response: {e}")
            if should_search:
                return "I'll help you find the perfect car! Let me search for some options."
            else:
                return "I'm here to help you find your ideal car! What kind of vehicle are you looking for?"
    
    def update_conversation_with_search_results(self, user_id: str, search_query: str, listings: List[Dict], analysis: str) -> str:
        """Update conversation with search results and generate follow-up response"""
        try:
            # Save search results
            self.conversation_manager.save_search_results(user_id, search_query, listings)
            
            # Generate follow-up response
            conversation_history = self.conversation_manager.get_conversation_history(user_id)
            
            follow_up_prompt = f"""Based on the car search results I just provided, generate a helpful follow-up response. 
            The search found {len(listings)} cars. Be encouraging and ask if they'd like to refine their search or see more details about any specific car."""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": follow_up_prompt},
                    {"role": "user", "content": f"I found {len(listings)} cars for you. Here's what I found: {analysis[:200]}..."}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            follow_up_response = response.choices[0].message.content.strip()
            
            # Add assistant response to conversation
            self.conversation_manager.add_message(user_id, "assistant", follow_up_response)
            
            return follow_up_response
            
        except Exception as e:
            print(f"Error updating conversation with search results: {e}")
            return "I found some great options for you! Would you like to refine your search or see more details about any specific car?"


