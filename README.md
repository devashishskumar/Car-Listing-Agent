# 🚗 Car Listing Viewing Agent

A simple yet powerful AI-powered agent that helps you find car listings from the web based on your natural language queries.

## Features

- **🌐 Modern Web Interface**: Beautiful, responsive web application with real-time search
- **🤖 Natural Language Processing**: Use OpenAI GPT to understand your car search queries
- **🕷️ Web Scraping**: Searches multiple car listing websites (Cars.com, AutoTrader)
- **🧠 Intelligent Analysis**: Provides AI-powered insights about found listings
- **💻 Multiple Interfaces**: Web interface, command-line, and interactive modes
- **🔍 Flexible Queries**: Search by make, model, year, price, features, and more
- **📱 Responsive Design**: Works perfectly on desktop, tablet, and mobile devices

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up your OpenAI API Key

Create a `.env` file in the project directory:

```bash
echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
```

Replace `your_actual_api_key_here` with your actual OpenAI API key.

### 3. Run the Agent

#### 🌐 Web Interface (Recommended)
```bash
python app.py
```
Then open your browser and go to: **http://localhost:8080**

#### 💻 Command Line Interface
```bash
# Interactive Mode
python car_agent.py

# Command Line Mode
python car_agent.py "Find me a Honda Civic under $20,000"
```

## 🌐 Web Interface Features

The web interface provides two modes for interacting with the Car Listing Agent:

### 🔍 Search Mode (`/`)
A modern, user-friendly search experience:

- **🎨 Beautiful Design**: Modern gradient UI with smooth animations
- **⚡ Real-time Search**: Instant feedback and loading indicators
- **📱 Responsive Layout**: Works on all screen sizes
- **🔍 Smart Search**: Enhanced query processing with AI
- **📊 Rich Results**: Detailed listings with AI analysis
- **⌨️ Keyboard Shortcuts**: Ctrl+K to focus search, Enter to search
- **🎯 Example Queries**: Click-to-search example queries
- **❓ Help System**: Built-in help and about modals

### 💬 Chat Mode (`/chat`)
A conversational interface for natural interaction:

- **🤖 Conversational AI**: Natural chat experience with the AI assistant
- **🧠 Context Awareness**: Remembers conversation history and preferences
- **🎯 Smart Intent Recognition**: Automatically detects when you want to search for cars
- **⚡ Quick Actions**: Pre-defined buttons for common car searches
- **⌨️ Typing Indicators**: Shows when the AI is responding
- **📱 Modal Results**: Car listings displayed in a beautiful modal overlay
- **🔄 New Chat**: Start fresh conversations anytime
- **📊 Real-time Analysis**: AI provides insights about found listings

### Web Interface Screenshots
- Clean, modern search interface
- Detailed car listings with prices and mileage
- AI-powered analysis and recommendations
- Mobile-responsive design

## Example Queries

### 🔍 Search Mode Queries
Direct search queries that immediately return car listings:

- `"Find me a Honda Civic under $20,000"`
- `"Looking for a BMW X3 with low mileage"`
- `"Toyota Camry 2020 or newer"`
- `"Electric car under $30,000"`
- `"Ford F-150 pickup truck"`
- `"Luxury sedan with leather seats"`

### 💬 Chat Mode Conversations
Natural conversations that can lead to car searches:

- `"Hi, I'm looking for a reliable car"`
- `"What's the best SUV under $25,000?"`
- `"I need help finding a family car"`
- `"Can you recommend a good Honda?"`
- `"I'm interested in electric vehicles"`
- `"What should I look for when buying a used car?"`

## How It Works

1. **Query Processing**: Your natural language query is processed by OpenAI GPT to extract key search parameters
2. **Web Scraping**: The agent searches multiple car listing websites using the extracted parameters
3. **Results Display**: Found listings are displayed with key information (price, mileage, location, source)
4. **AI Analysis**: OpenAI provides intelligent analysis and recommendations based on the found listings

## Project Structure

```
Car Agent/
├── app.py                    # Flask web application
├── car_agent.py              # Command-line agent script
├── car_scraper.py            # Web scraping functionality
├── ai_processor.py           # OpenAI integration for query processing
├── conversation_manager.py   # Chat conversation management
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── templates/                # HTML templates
│   ├── index.html           # Search interface
│   └── chat.html            # Chat interface
├── static/                  # Static web assets
│   ├── css/
│   │   ├── style.css        # Search interface styles
│   │   └── chat.css         # Chat interface styles
│   └── js/
│       ├── app.js           # Search interface JavaScript
│       └── chat.js          # Chat interface JavaScript
├── setup.py           # Easy setup script
├── demo.py            # Demo script
└── README.md          # This file
```

## Dependencies

- `requests`: For web scraping
- `beautifulsoup4`: For HTML parsing
- `openai`: For AI query processing
- `python-dotenv`: For environment variable management
- `fake-useragent`: For rotating user agents

## Notes

- The agent respects website terms of service by using appropriate delays between requests
- Results may vary based on website availability and structure changes
- The AI analysis provides helpful insights but should be used as guidance, not absolute recommendations

## Troubleshooting

1. **"OpenAI API key not found"**: Make sure your `.env` file exists and contains your API key
2. **"No listings found"**: Try adjusting your search criteria or check your internet connection
3. **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

## License

This project is for educational and personal use. Please respect the terms of service of the websites being scraped.
