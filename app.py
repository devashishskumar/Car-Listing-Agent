#!/usr/bin/env python3
"""
Flask Web Application for Car Listing Agent
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from car_scraper import CarScraper
from ai_processor import AIProcessor
from config import Config

app = Flask(__name__)
CORS(app)

# Initialize the agent components
try:
    scraper = CarScraper()
    ai_processor = AIProcessor()
    print("🚗 Car Listing Agent Web App initialized successfully!")
except Exception as e:
    print(f"❌ Error initializing web app: {e}")
    scraper = None
    ai_processor = None

@app.route('/')
def index():
    """Main page - Search interface"""
    return render_template('index.html')

@app.route('/chat')
def chat_page():
    """Chat interface page"""
    return render_template('chat.html')

@app.route('/search', methods=['POST'])
def search_cars():
    """API endpoint for car search"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        if not scraper or not ai_processor:
            return jsonify({'error': 'Agent not properly initialized'}), 500
        
        # Process the query
        enhanced_query = ai_processor.enhance_search_query(query)
        listings = scraper.search_all_sites(enhanced_query)
        
        # Get AI analysis
        analysis = ai_processor.analyze_listings(listings, query)
        
        response = {
            'success': True,
            'query': query,
            'enhanced_query': enhanced_query,
            'listings': listings,
            'analysis': analysis,
            'total_found': len(listings)
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    """API endpoint for conversational chat"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        user_id = data.get('user_id', 'default')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not ai_processor:
            return jsonify({'error': 'Agent not properly initialized'}), 500
        
        # Process conversational message
        result = ai_processor.process_conversational_message(message, user_id)
        
        response = {
            'success': True,
            'type': result['type'],
            'response': result['response'],
            'search_query': result.get('search_query'),
            'criteria': result.get('criteria')
        }
        
        # If it's a search request, perform the search
        if result['type'] == 'search_request' and result['search_query']:
            try:
                enhanced_query = ai_processor.enhance_search_query(result['search_query'])
                listings = scraper.search_all_sites(enhanced_query)
                analysis = ai_processor.analyze_listings(listings, result['search_query'])
                
                # Generate follow-up response
                follow_up = ai_processor.update_conversation_with_search_results(
                    user_id, result['search_query'], listings, analysis
                )
                
                response.update({
                    'listings': listings,
                    'analysis': analysis,
                    'total_found': len(listings),
                    'follow_up': follow_up
                })
                
            except Exception as e:
                print(f"Error performing search: {e}")
                response['search_error'] = "I found your search criteria, but encountered an error while searching. Please try again."
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/start-conversation', methods=['POST'])
def start_conversation():
    """API endpoint to start a new conversation"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default')
        
        if not ai_processor:
            return jsonify({'error': 'Agent not properly initialized'}), 500
        
        # Start new conversation
        welcome_message = ai_processor.conversation_manager.start_conversation(user_id)
        
        return jsonify({
            'success': True,
            'welcome_message': welcome_message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'scraper_available': scraper is not None,
        'ai_processor_available': ai_processor is not None
    })

if __name__ == '__main__':
    print("🌐 Starting Car Listing Agent Web App...")
    print("📱 Open your browser and go to: http://localhost:8080")
    app.run(debug=True, host='0.0.0.0', port=8080)
