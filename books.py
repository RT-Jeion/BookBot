# books.py
import requests
from bs4 import BeautifulSoup
import json
import os
import re
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta

# Enhanced logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "https://books.toscrape.com"
CATALOG_URL = f"{BASE_URL}/catalogue/page-1.html"
CACHE_FILE = "book_cache.json"
CACHE_EXPIRY = timedelta(hours=24)
GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"

class BookCache:
    def __init__(self, filename: str):
        self.filename = filename
        self.cache = self.load()
    
    def load(self) -> dict:
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Check cache freshness
                    if data.get('timestamp'):
                        cache_time = datetime.fromisoformat(data['timestamp'])
                        if datetime.now() - cache_time > CACHE_EXPIRY:
                            return {"books": [], "timestamp": None}
                    return data
        except Exception as e:
            logger.error(f"Cache load error: {e}")
        return {"books": [], "timestamp": None}
    
    def save(self, books: List[dict]):
        try:
            cache = {
                "books": books,
                "timestamp": datetime.now().isoformat(),
                "count": len(books)
            }
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Cache save error: {e}")

def search_google_books(query: str, limit: int = 3) -> List[dict]:
    """Fallback to Google Books API"""
    try:
        params = {
            "q": query,
            "maxResults": limit,
            "langRestrict": "en"
        }
        response = requests.get(GOOGLE_BOOKS_API, params=params, timeout=10)
        response.raise_for_status()
        items = response.json().get("items", [])
        
        results = []
        for item in items:
            info = item.get("volumeInfo", {})
            sale = item.get("saleInfo", {})
            
            book = {
                "title": info.get("title", "Unknown Title"),
                "authors": ", ".join(info.get("authors", ["Unknown Author"])),
                "description": info.get("description", "No description available"),
                "isbn": next((i.get("identifier") for i in info.get("industryIdentifiers", []) 
                            if i.get("type") in ["ISBN_13", "ISBN_10"]), "N/A"),
                "price": f"£{sale.get('retailPrice', {}).get('amount', 0):.2f}" 
                        if sale.get('retailPrice') else "N/A",
                "in_stock": sale.get("saleability") == "FOR_SALE",
                "url": info.get("infoLink", ""),
                "image": info.get("imageLinks", {}).get("thumbnail", "")
            }
            results.append(book)
        return results
    except Exception as e:
        logger.error(f"Google Books API error: {e}")
        return []

# === LOAD / SAVE CACHE ===
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"books": [], "last_scrape": None}

def save_cache(data):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# === SCRAPE CATALOG (First Page Only for Prototype) ===
def scrape_catalog(max_pages=5):
    """Scrape multiple pages of books"""
    print("Scraping books.toscrape.com...")
    all_books = []
    
    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/catalogue/page-{page}.html"
        try:
            headers = {"User-Agent": "Mozilla/5.0 (BookBot Prototype)"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            book_articles = soup.find_all('article', class_='product_pod')
            
            if not book_articles:
                break
                
            for article in book_articles:
                title = article.h3.a['title']
                price = article.find('p', class_='price_color').text
                url = article.find('a')['href']
                
                book = {
                    'title': title,
                    'price': price,
                    'url': f"{BASE_URL}/catalogue/{url}",
                    'authors': 'Unknown Author',  # Will be updated later
                    'isbn': None,
                    'description': None
                }
                all_books.append(book)
            
            print(f"✓ Page {page}: Found {len(book_articles)} books")
            
        except Exception as e:
            logger.error(f"Error scraping page {page}: {e}")
            break
    
    print(f"Total books scraped: {len(all_books)}")
    return all_books

# === FETCH FULL BOOK DETAILS (Author, ISBN, Description) ===
def fetch_book_details(book_url):
    if not book_url:
        return {}
    try:
        headers = {"User-Agent": "Mozilla/5.0 (BookBot Prototype)"}
        response = requests.get(book_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Author (from table or breadcrumb)
        author = "Unknown Author"
        author_tag = soup.find('th', string='Author')
        if author_tag:
            author = author_tag.find_next('td').get_text(strip=True)
        
        # ISBN (UPC is used as ISBN on this site)
        isbn = None
        isbn_tag = soup.find('th', string='UPC')
        if isbn_tag:
            isbn = isbn_tag.find_next('td').get_text(strip=True)
        
        # Description
        desc_tag = soup.find('div', id='product_description')
        description = desc_tag.find_next('p').get_text(strip=True) if desc_tag else None
        
        return {
            "author": author,
            "isbn": isbn,
            "description": description
        }
    except Exception as e:
        print("Detail fetch failed:", str(e))
        return {}

# Main search function
def search_books(query: str, limit: int = 3) -> List[dict]:
    """
    Enhanced book search with multiple sources and better caching
    """
    cache = BookCache(CACHE_FILE)
    cached_books = cache.load().get("books", [])
    
    # Try cache first
    if cached_books:
        matches = [b for b in cached_books 
                  if query.lower() in b["title"].lower()]
        if matches:
            return matches[:limit]
    
    # Try scraping
    logger.info(f"Searching for: {query}")
    books = scrape_catalog()
    if books:
        cache.save(books)
        matches = [b for b in books 
                  if query.lower() in b["title"].lower()]
        if matches:
            # Enhance with details
            for book in matches[:limit]:
                if not book.get("author"):
                    details = fetch_book_details(book["url"])
                    book.update(details)
            return matches[:limit]
    
    # Fallback to Google Books
    logger.info("Falling back to Google Books API")
    return search_google_books(query, limit)

# === TEST WHEN RUN DIRECTLY ===
if __name__ == "__main__":
    # Enhanced testing
    print("Testing enhanced books.py...")
    
    queries = [
        "Python Programming",
        "Atomic Habits",
        "নোবেল প্রাইজ"  # Test non-English
    ]
    
    for query in queries:
        print(f"\nSearching for: {query}")
        results = search_books(query, limit=2)
        for i, book in enumerate(results, 1):
            print(f"\n{i}. Title: {book['title']}")
            print(f"   Author(s): {book.get('authors', 'N/A')}")
            print(f"   Price: {book.get('price', 'N/A')}")
            print(f"   ISBN: {book.get('isbn', 'N/A')}")
            print(f"   In Stock: {book.get('in_stock', False)}")