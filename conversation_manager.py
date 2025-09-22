#!/usr/bin/env python3
"""
Conversation Manager for Car Listing Agent
Handles chat history, context, and conversational flow
"""

from typing import List, Dict, Optional
import json
from datetime import datetime

class ConversationManager:
    def __init__(self):
        self.conversations = {}
        self.system_prompt = """You are a helpful car buying assistant. You help users find cars by:

1. Understanding their needs through conversation
2. Asking clarifying questions when needed
3. Providing car recommendations based on their criteria
4. Explaining car features and pricing
5. Helping them refine their search

Be friendly, conversational, and helpful. Always try to understand what the user is looking for before suggesting cars."""

    def start_conversation(self, user_id: str = "default") -> str:
        """Start a new conversation"""
        self.conversations[user_id] = {
            "messages": [
                {
                    "role": "system",
                    "content": self.system_prompt,
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "role": "assistant", 
                    "content": "Hi! I'm your car buying assistant. I can help you find the perfect car! What kind of vehicle are you looking for?",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "last_search": None,
            "search_history": [],
            "created_at": datetime.now().isoformat()
        }
        return self.conversations[user_id]["messages"][-1]["content"]

    def add_message(self, user_id: str, role: str, content: str) -> None:
        """Add a message to the conversation"""
        if user_id not in self.conversations:
            self.start_conversation(user_id)
        
        self.conversations[user_id]["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_conversation_history(self, user_id: str) -> List[Dict]:
        """Get conversation history for context"""
        if user_id not in self.conversations:
            return []
        return self.conversations[user_id]["messages"]

    def get_last_search(self, user_id: str) -> Optional[Dict]:
        """Get the last search performed"""
        if user_id not in self.conversations:
            return None
        return self.conversations[user_id].get("last_search")

    def save_search_results(self, user_id: str, query: str, results: List[Dict]) -> None:
        """Save search results to conversation history"""
        if user_id not in self.conversations:
            self.start_conversation(user_id)
        
        search_data = {
            "query": query,
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "count": len(results)
        }
        
        self.conversations[user_id]["last_search"] = search_data
        self.conversations[user_id]["search_history"].append(search_data)

    def should_search_for_cars(self, message: str, conversation_history: List[Dict]) -> bool:
        """Determine if the user wants to search for cars"""
        message_lower = message.lower()
        
        # Keywords that indicate car search intent
        search_keywords = [
            "find", "search", "looking for", "want", "need", "show me", 
            "honda", "toyota", "ford", "bmw", "mercedes", "audi", "nissan",
            "civic", "camry", "accord", "corolla", "mustang", "pilot",
            "under", "budget", "price", "mileage", "year", "model",
            "car", "vehicle", "auto", "automobile", "sedan", "suv", "truck"
        ]
        
        # Check if message contains car-related keywords
        has_car_keywords = any(keyword in message_lower for keyword in search_keywords)
        
        # Check for direct search requests
        search_requests = [
            "search for", "find cars", "show cars", "car listings",
            "what cars", "available cars", "car options"
        ]
        
        has_search_request = any(request in message_lower for request in search_requests)
        
        return has_car_keywords or has_search_request

    def extract_car_criteria(self, message: str) -> Dict:
        """Extract car search criteria from user message"""
        criteria = {
            "make": None,
            "model": None,
            "year_min": None,
            "year_max": None,
            "price_max": None,
            "price_min": None,
            "mileage_max": None,
            "features": [],
            "body_type": None
        }
        
        message_lower = message.lower()
        
        # Extract make and model
        makes = ['honda', 'toyota', 'ford', 'chevrolet', 'nissan', 'bmw', 'mercedes', 
                'audi', 'lexus', 'acura', 'infiniti', 'volkswagen', 'hyundai', 'kia',
                'mazda', 'subaru', 'jeep', 'dodge', 'chrysler', 'buick', 'cadillac']
        
        for make in makes:
            if make in message_lower:
                criteria["make"] = make
                break
        
        # Extract price information
        import re
        price_patterns = [
            r'under\s+\$?([\d,]+)',
            r'less\s+than\s+\$?([\d,]+)',
            r'below\s+\$?([\d,]+)',
            r'max\s+\$?([\d,]+)',
            r'budget\s+of\s+\$?([\d,]+)',
            r'\$?([\d,]+)\s*-\s*\$?([\d,]+)',  # price range
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, message_lower)
            if match:
                if len(match.groups()) == 2:  # price range
                    criteria["price_min"] = int(match.group(1).replace(',', ''))
                    criteria["price_max"] = int(match.group(2).replace(',', ''))
                else:  # max price
                    criteria["price_max"] = int(match.group(1).replace(',', ''))
                break
        
        # Extract year information
        year_patterns = [
            r'(\d{4})\s*or\s*newer',
            r'(\d{4})\s*and\s*up',
            r'after\s+(\d{4})',
            r'from\s+(\d{4})',
            r'(\d{4})\s*-\s*(\d{4})',  # year range
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, message_lower)
            if match:
                if len(match.groups()) == 2:  # year range
                    criteria["year_min"] = int(match.group(1))
                    criteria["year_max"] = int(match.group(2))
                else:  # min year
                    criteria["year_min"] = int(match.group(1))
                break
        
        # Extract mileage information
        mileage_patterns = [
            r'under\s+([\d,]+)\s*miles?',
            r'less\s+than\s+([\d,]+)\s*miles?',
            r'below\s+([\d,]+)\s*miles?',
            r'max\s+([\d,]+)\s*miles?',
            r'low\s+mileage',
        ]
        
        for pattern in mileage_patterns:
            match = re.search(pattern, message_lower)
            if match:
                if 'low mileage' in message_lower:
                    criteria["mileage_max"] = 50000  # assume low mileage means under 50k
                else:
                    criteria["mileage_max"] = int(match.group(1).replace(',', ''))
                break
        
        # Extract features
        features = ['automatic', 'manual', 'awd', '4wd', 'leather', 'sunroof', 
                   'bluetooth', 'backup camera', 'heated seats', 'navigation']
        
        for feature in features:
            if feature in message_lower:
                criteria["features"].append(feature)
        
        # Extract body type
        body_types = ['sedan', 'suv', 'truck', 'hatchback', 'coupe', 'convertible', 'wagon']
        for body_type in body_types:
            if body_type in message_lower:
                criteria["body_type"] = body_type
                break
        
        return criteria

    def generate_search_query(self, criteria: Dict) -> str:
        """Generate a search query from extracted criteria"""
        query_parts = []
        
        if criteria["make"]:
            query_parts.append(criteria["make"].title())
        
        if criteria["model"]:
            query_parts.append(criteria["model"].title())
        
        if criteria["year_min"]:
            query_parts.append(f"{criteria['year_min']} or newer")
        
        if criteria["price_max"]:
            query_parts.append(f"under ${criteria['price_max']:,}")
        
        if criteria["mileage_max"]:
            query_parts.append(f"under {criteria['mileage_max']:,} miles")
        
        if criteria["body_type"]:
            query_parts.append(criteria["body_type"])
        
        if criteria["features"]:
            query_parts.extend(criteria["features"])
        
        return " ".join(query_parts) if query_parts else "cars"

    def get_conversation_summary(self, user_id: str) -> Dict:
        """Get a summary of the current conversation"""
        if user_id not in self.conversations:
            return {"message_count": 0, "searches_performed": 0}
        
        conv = self.conversations[user_id]
        return {
            "message_count": len(conv["messages"]) - 2,  # exclude system and initial assistant message
            "searches_performed": len(conv["search_history"]),
            "last_search": conv.get("last_search"),
            "created_at": conv["created_at"]
        }

