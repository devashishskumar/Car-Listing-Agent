import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict
import time
import random
import json
from urllib.parse import urlencode, urlparse, parse_qs
from config import Config

try:
    from fake_useragent import UserAgent
    FAKE_USERAGENT_AVAILABLE = True
except ImportError:
    FAKE_USERAGENT_AVAILABLE = False
    print("Warning: fake_useragent not available, using default user agent")

class CarScraper:
    def __init__(self):
        # Multiple user agents for rotation
        self.user_agents = [
            # Chrome on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Chrome on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Firefox on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            # Safari on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            # Edge on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            # Mobile Chrome
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.216 Mobile/15E148 Safari/604.1',
            # Mobile Safari
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
        ]
        
        # Initialize fake user agent if available
        if FAKE_USERAGENT_AVAILABLE:
            try:
                self.ua = UserAgent()
                self.user_agents.extend([
                    self.ua.chrome,
                    self.ua.firefox,
                    self.ua.safari,
                    self.ua.edge
                ])
            except:
                pass
        
        # Create session with better configuration
        self.session = requests.Session()
        
        # Configure session with retries and timeouts
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self._update_headers()
        
        # Cookie jar for session persistence
        self.session.cookies.clear()
        
        # Track request patterns
        self.request_count = 0
        self.last_request_time = 0
    
    def _update_headers(self):
        """Update headers with random user agent and realistic browser headers"""
        user_agent = random.choice(self.user_agents)
        
        # Determine if mobile based on user agent
        is_mobile = any(mobile in user_agent.lower() for mobile in ['mobile', 'iphone', 'android'])
        
        if is_mobile:
            self.headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            }
        else:
            self.headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
        
        self.session.headers.update(self.headers)
    
    def _smart_delay(self):
        """Implement smart delays to avoid rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Minimum delay between requests
        min_delay = random.uniform(2, 5)
        
        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
        
        # Longer delay every 5 requests
        if self.request_count % 5 == 0:
            time.sleep(random.uniform(5, 10))
    
    def _make_request(self, url: str, max_retries: int = 3) -> requests.Response:
        """Make HTTP request with retries and better error handling"""
        for attempt in range(max_retries):
            try:
                # Update headers with new user agent for each attempt
                if attempt > 0:
                    self._update_headers()
                
                # Smart delay to avoid rate limiting
                self._smart_delay()
                
                print(f"Making request to: {url}")
                print(f"Using User-Agent: {self.headers['User-Agent'][:50]}...")
                
                # Make request with longer timeout
                response = self.session.get(url, timeout=30, allow_redirects=True)
                
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {dict(list(response.headers.items())[:3])}")
                
                # Check for redirects
                if response.history:
                    print(f"Redirected from: {response.history[0].url}")
                    print(f"Final URL: {response.url}")
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.Timeout:
                print(f"Timeout on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
            except requests.exceptions.HTTPError as e:
                print(f"HTTP error on attempt {attempt + 1}/{max_retries}: {e}")
                if e.response.status_code == 429:  # Rate limited
                    print("Rate limited, waiting longer...")
                    time.sleep(random.uniform(10, 20))
                elif attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue
            except requests.exceptions.RequestException as e:
                print(f"Request error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue
        
        raise requests.exceptions.RequestException("Max retries exceeded")

    def search_cars_com(self, query: str) -> List[Dict]:
        """Search cars.com for listings with improved parsing"""
        listings = []
        try:
            # Parse query for make and model
            make, model = self._parse_car_query(query)
            
            # Try multiple URL patterns for cars.com
            url_patterns = [
                # Pattern 1: Standard search
                f"https://www.cars.com/shopping/results/?zip=75001&maximum_distance=50&makes[]={make.lower()}",
                # Pattern 2: With model
                f"https://www.cars.com/shopping/results/?zip=75001&maximum_distance=50&makes[]={make.lower()}&models[]={model.lower()}" if model else None,
                # Pattern 3: Alternative format
                f"https://www.cars.com/shopping/results/?dealer_id=&list_price_max=&list_price_min=&makes[]={make.lower()}&maximum_distance=50&mileage_max=&page_size=20&sort=best_match_desc&stock_type=all&zip=75001",
                # Pattern 4: Mobile format
                f"https://www.cars.com/shopping/results/?zip=75001&maximum_distance=50&makes[]={make.lower()}&mobile=true"
            ]
            
            # Filter out None values
            url_patterns = [url for url in url_patterns if url is not None]
            
            for url in url_patterns:
                try:
                    print(f"Trying cars.com URL: {url}")
                    response = self._make_request(url)
                    soup = BeautifulSoup(response.content, 'lxml')  # Use lxml parser for better performance
                    
                    # Save HTML for debugging
                    with open('cars_com_debug.html', 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    
                    # Try multiple comprehensive selectors
                    car_selectors = [
                        # Modern selectors
                        'div[data-qa="vehicle-card"]',
                        'div[data-cmp="vehicle-card"]',
                        'div.vehicle-card',
                        'article[data-qa="vehicle-card"]',
                        'article.vehicle-card',
                        
                        # Generic selectors
                        'div[class*="vehicle-card"]',
                        'div[class*="listing"]',
                        'div[class*="result"]',
                        'article[class*="vehicle"]',
                        'article[class*="listing"]',
                        
                        # Data attributes
                        'div[data-testid*="vehicle"]',
                        'div[data-testid*="listing"]',
                        'div[data-testid*="card"]',
                        
                        # Generic containers
                        'div[class*="card"]',
                        'div[class*="item"]',
                        'div[class*="product"]',
                        
                        # Fallback selectors
                        'div[role="article"]',
                        'div[role="listitem"]',
                        'div[aria-label*="vehicle"]',
                        'div[aria-label*="car"]'
                    ]
                    
                    cars = []
                    used_selector = None
                    
                    for selector in car_selectors:
                        cars = soup.select(selector)
                        if cars and len(cars) > 2:  # Need at least a few results
                            used_selector = selector
                            print(f"✅ Found {len(cars)} cars using selector: {selector}")
                            break
                    
                    if not cars:
                        print("❌ No cars found with standard selectors, trying alternative approach...")
                        # Try to find any elements with car-related text or attributes
                        cars = soup.find_all(['div', 'article'], 
                                           attrs={'class': re.compile(r'.*(car|vehicle|listing|result|item|card).*', re.I)})
                        
                        if not cars:
                            # Last resort: find any div with price-like content
                            cars = soup.find_all('div', string=re.compile(r'\$[\d,]+'))
                        
                        print(f"Alternative search found {len(cars)} potential listings")
                    
                    if cars:
                        print(f"Parsing {len(cars)} car listings...")
                        for i, car in enumerate(cars[:15]):  # Limit to 15 results
                            try:
                                listing = self._parse_cars_com_listing(car, i + 1)
                                if listing and listing['title'] != 'N/A':
                                    listings.append(listing)
                                    print(f"✅ Parsed listing {i+1}: {listing['title'][:50]}...")
                            except Exception as e:
                                print(f"❌ Error parsing listing {i+1}: {e}")
                                continue
                        
                        if listings:
                            print(f"✅ Successfully scraped {len(listings)} listings from cars.com")
                            break  # Success, no need to try other URLs
                    
                except Exception as e:
                    print(f"❌ Error with URL pattern: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error scraping cars.com: {e}")
            
        return listings
    
    def _parse_cars_com_listing(self, car_element, index: int) -> Dict:
        """Parse individual car listing from cars.com with multiple strategies"""
        listing = {
            'title': 'N/A',
            'price': 'N/A', 
            'mileage': 'N/A',
            'location': 'N/A',
            'url': 'N/A',
            'source': 'cars.com'
        }
        
        try:
            # Strategy 1: Try to find title
            title_selectors = [
                'h2[data-qa="vehicle-title"]',
                'h3[data-qa="vehicle-title"]',
                'h2.vehicle-title',
                'h3.vehicle-title',
                'h2[class*="title"]',
                'h3[class*="title"]',
                'a[data-qa="vehicle-title"]',
                'a[class*="title"]',
                'span[data-qa="vehicle-title"]',
                'div[data-qa="vehicle-title"]',
                'h1', 'h2', 'h3',
                'a[href*="/vehicledetail/"]',
                'a[href*="/shopping/"]'
            ]
            
            title_elem = None
            for selector in title_selectors:
                title_elem = car_element.select_one(selector)
                if title_elem:
                    break
            
            if title_elem:
                listing['title'] = title_elem.get_text(strip=True)
            else:
                # Fallback: find any text that looks like a car title
                text_elements = car_element.find_all(text=True)
                for text in text_elements:
                    text = text.strip()
                    if (len(text) > 10 and len(text) < 100 and 
                        any(word in text.lower() for word in ['honda', 'toyota', 'ford', 'bmw', 'mercedes', 'audi', 'nissan', 'chevrolet'])):
                        listing['title'] = text
                        break
            
            # Strategy 2: Try to find price
            price_selectors = [
                'span[data-qa="primary-price"]',
                'div[data-qa="primary-price"]',
                'span.primary-price',
                'div.primary-price',
                'span[class*="price"]',
                'div[class*="price"]',
                'span[class*="cost"]',
                'div[class*="cost"]',
                'span[data-qa="price"]',
                'div[data-qa="price"]'
            ]
            
            price_elem = None
            for selector in price_selectors:
                price_elem = car_element.select_one(selector)
                if price_elem:
                    break
            
            if price_elem:
                listing['price'] = price_elem.get_text(strip=True)
            else:
                # Fallback: find any text with dollar sign
                price_text = car_element.find(text=re.compile(r'\$[\d,]+'))
                if price_text:
                    listing['price'] = price_text.strip()
            
            # Strategy 3: Try to find mileage
            mileage_selectors = [
                'div[data-qa="mileage"]',
                'span[data-qa="mileage"]',
                'div.mileage',
                'span.mileage',
                'div[class*="mileage"]',
                'span[class*="mileage"]',
                'div[class*="mile"]',
                'span[class*="mile"]'
            ]
            
            mileage_elem = None
            for selector in mileage_selectors:
                mileage_elem = car_element.select_one(selector)
                if mileage_elem:
                    break
            
            if mileage_elem:
                listing['mileage'] = mileage_elem.get_text(strip=True)
            else:
                # Fallback: find any text with "mile"
                mileage_text = car_element.find(text=re.compile(r'[\d,]+.*mile', re.I))
                if mileage_text:
                    listing['mileage'] = mileage_text.strip()
            
            # Strategy 4: Try to find location
            location_selectors = [
                'div[data-qa="dealer-name"]',
                'span[data-qa="dealer-name"]',
                'div.dealer-name',
                'span.dealer-name',
                'div[class*="dealer"]',
                'span[class*="dealer"]',
                'div[class*="location"]',
                'span[class*="location"]',
                'div[class*="city"]',
                'span[class*="city"]'
            ]
            
            location_elem = None
            for selector in location_selectors:
                location_elem = car_element.select_one(selector)
                if location_elem:
                    break
            
            if location_elem:
                listing['location'] = location_elem.get_text(strip=True)
            
            # Strategy 5: Try to find URL/link
            url_selectors = [
                'a[data-qa="vehicle-title"]',
                'a[href*="/vehicledetail/"]',
                'a[href*="/shopping/"]',
                'a[href*="/cars/"]',
                'a[class*="title"]',
                'a[class*="vehicle"]',
                'a'
            ]
            
            url_elem = None
            for selector in url_selectors:
                url_elem = car_element.select_one(selector)
                if url_elem and url_elem.get('href'):
                    break
            
            if url_elem and url_elem.get('href'):
                href = url_elem.get('href')
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    listing['url'] = f"https://www.cars.com{href}"
                elif href.startswith('http'):
                    listing['url'] = href
                else:
                    listing['url'] = f"https://www.cars.com/{href}"
            
            # Clean up the data
            for key in ['title', 'price', 'mileage', 'location']:
                if listing[key] != 'N/A':
                    listing[key] = re.sub(r'\s+', ' ', listing[key]).strip()
            
        except Exception as e:
            print(f"Error parsing listing {index}: {e}")
        
        return listing
    
    def search_autotrader(self, query: str) -> List[Dict]:
        """Search AutoTrader for listings"""
        listings = []
        try:
            make, model = self._parse_car_query(query)
            
            # Build search URL for AutoTrader with better structure
            base_url = "https://www.autotrader.com/cars-for-sale/all-cars"
            url = f"{base_url}?makeCode={make.upper()}&zip=75001&radius=50"
            if model:
                url += f"&modelCodeList={model.upper()}"
            
            print(f"Searching autotrader.com with URL: {url}")
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple possible selectors for car listings
            car_selectors = [
                'div[data-cmp="inventoryListing"]',
                'div.inventory-listing',
                'div[class*="inventory-listing"]',
                'div[class*="listing"]',
                'article[data-cmp="inventoryListing"]'
            ]
            
            cars = []
            for selector in car_selectors:
                cars = soup.select(selector)
                if cars:
                    print(f"Found {len(cars)} cars using selector: {selector}")
                    break
            
            if not cars:
                print("No car listings found on AutoTrader. Website structure may have changed.")
                # Try to find any car-related content
                cars = soup.find_all(['div', 'article'], class_=re.compile(r'.*(car|vehicle|listing).*', re.I))
                print(f"Alternative search found {len(cars)} potential listings")
            
            for car in cars[:10]:
                try:
                    # Try multiple selectors for each field
                    title_elem = (car.find(['h1', 'h2', 'h3'], class_=re.compile(r'.*(title|name|heading).*', re.I)) or 
                                car.find(['h1', 'h2', 'h3']) or
                                car.find('a', class_=re.compile(r'.*(title|name).*', re.I)))
                    
                    price_elem = (car.find(['span', 'div'], class_=re.compile(r'.*(price|cost).*', re.I)) or
                                car.find(['span', 'div'], string=re.compile(r'\$[\d,]+')))
                    
                    mileage_elem = (car.find(['span', 'div'], class_=re.compile(r'.*(mile|odometer).*', re.I)) or
                                  car.find(['span', 'div'], string=re.compile(r'[\d,]+.*mile', re.I)))
                    
                    location_elem = (car.find(['span', 'div'], class_=re.compile(r'.*(location|dealer|city).*', re.I)) or
                                   car.find(['span', 'div'], class_=re.compile(r'.*(address|place).*', re.I)))
                    
                    listing = {
                        'title': title_elem.get_text(strip=True) if title_elem else 'N/A',
                        'price': price_elem.get_text(strip=True) if price_elem else 'N/A',
                        'mileage': mileage_elem.get_text(strip=True) if mileage_elem else 'N/A',
                        'location': location_elem.get_text(strip=True) if location_elem else 'N/A',
                        'source': 'autotrader.com'
                    }
                    listings.append(listing)
                except Exception as e:
                    print(f"Error parsing individual listing: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping autotrader.com: {e}")
            
        return listings
    
    def _parse_car_query(self, query: str) -> tuple:
        """Parse user query to extract make and model"""
        query_lower = query.lower()
        
        # Common car makes
        makes = ['toyota', 'honda', 'ford', 'chevrolet', 'nissan', 'bmw', 'mercedes', 
                'audi', 'lexus', 'acura', 'infiniti', 'volkswagen', 'hyundai', 'kia',
                'mazda', 'subaru', 'jeep', 'dodge', 'chrysler', 'buick', 'cadillac',
                'lincoln', 'volvo', 'saab', 'porsche', 'ferrari', 'lamborghini',
                'maserati', 'bentley', 'rolls-royce', 'tesla', 'genesis']
        
        make = None
        model = None
        
        # Find make in query
        for car_make in makes:
            if car_make in query_lower:
                make = car_make
                break
        
        # Try to extract model (usually comes after make)
        if make:
            make_index = query_lower.find(make)
            remaining_query = query_lower[make_index + len(make):].strip()
            words = remaining_query.split()
            if words:
                model = words[0]
        
        return make or 'honda', model
    
    def _generate_mock_listings(self, query: str) -> List[Dict]:
        """Generate mock listings when web scraping fails"""
        make, model = self._parse_car_query(query)
        
        mock_listings = [
            {
                'title': f'2020 {make.title()} {model.title()} - Clean Carfax',
                'price': '$18,500',
                'mileage': '45,000 miles',
                'location': 'Dallas, TX',
                'url': 'https://www.cars.com/vehicledetail/demo-1/',
                'source': 'Mock Data (Demo)'
            },
            {
                'title': f'2019 {make.title()} {model.title()} - Single Owner',
                'price': '$16,800',
                'mileage': '52,000 miles',
                'location': 'Austin, TX',
                'url': 'https://www.cars.com/vehicledetail/demo-2/',
                'source': 'Mock Data (Demo)'
            },
            {
                'title': f'2021 {make.title()} {model.title()} - Low Miles',
                'price': '$22,300',
                'mileage': '28,000 miles',
                'location': 'Houston, TX',
                'url': 'https://www.cars.com/vehicledetail/demo-3/',
                'source': 'Mock Data (Demo)'
            }
        ]
        
        return mock_listings

    def search_all_sites(self, query: str) -> List[Dict]:
        """Search all car listing websites"""
        all_listings = []
        
        try:
            # Search cars.com
            print("🔍 Searching cars.com...")
            cars_com_listings = self.search_cars_com(query)
            all_listings.extend(cars_com_listings)
            
            # Add delay between requests
            time.sleep(2)
            
            # Search AutoTrader
            print("🔍 Searching autotrader.com...")
            autotrader_listings = self.search_autotrader(query)
            all_listings.extend(autotrader_listings)
            
            # If no real listings found, provide mock data for demonstration
            if not all_listings:
                print("⚠️ No real listings found. Providing demo data...")
                all_listings = self._generate_mock_listings(query)
            
        except Exception as e:
            print(f"Error in search_all_sites: {e}")
            print("⚠️ Providing demo data due to scraping errors...")
            all_listings = self._generate_mock_listings(query)
        
        return all_listings
