"""
Web Scraper for Express Credit Union Website

This module scrapes the entire Express Credit Union website
and stores the content in the database for AI training.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import sqlite3
import config

# Set of visited URLs to avoid duplicates
visited_urls = set()

# Base URL for Express Credit Union
BASE_URL = "https://www.expresscu.org"

def is_valid_url(url):
    """Check if URL belongs to Express Credit Union website"""
    parsed = urlparse(url)
    return parsed.netloc == "www.expresscu.org" or parsed.netloc == "expresscu.org"

def get_all_links(url):
    """Extract all links from a webpage"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        links = set()
        for link in soup.find_all('a', href=True):
            full_url = urljoin(BASE_URL, link['href'])
            if is_valid_url(full_url):
                # Remove fragments (e.g., #section)
                full_url = full_url.split('#')[0]
                links.add(full_url)
        
        return links
    except Exception as e:
        print(f"Error getting links from {url}: {str(e)}")
        return set()

def scrape_page(url):
    """Scrape content from a single page"""
    try:
        print(f"Scraping: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get page title
        title = soup.title.string if soup.title else url
        
        # Get main content - try to find main content area
        main_content = soup.find('main') or soup.find('article') or soup.body
        
        if main_content:
            # Get all text from the page
            text = main_content.get_text(separator='\n', strip=True)
            
            # Clean up the text - remove excessive whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            content = '\n'.join(lines)
            
            return {
                'url': url,
                'title': title,
                'content': content
            }
        else:
            return None
            
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

def save_to_database(page_data):
    """Save scraped content to database"""
    try:
        conn = sqlite3.connect(config.DATABASE_NAME)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                content TEXT,
                scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert or replace content
        cursor.execute('''
            INSERT OR REPLACE INTO scraped_content (url, title, content, scraped_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (page_data['url'], page_data['title'], page_data['content']))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error saving to database: {str(e)}")

def scrape_website(max_pages=50):
    """
    Scrape the entire Express Credit Union website
    
    Args:
        max_pages: Maximum number of pages to scrape (to avoid infinite loops)
    """
    print("Starting web scraping...")
    print(f"Base URL: {BASE_URL}")
    print(f"Maximum pages: {max_pages}")
    print("-" * 60)
    
    # Start with the homepage
    to_visit = {BASE_URL}
    pages_scraped = 0
    
    while to_visit and pages_scraped < max_pages:
        url = to_visit.pop()
        
        # Skip if already visited
        if url in visited_urls:
            continue
        
        # Mark as visited
        visited_urls.add(url)
        
        # Scrape the page
        page_data = scrape_page(url)
        
        if page_data:
            # Save to database
            save_to_database(page_data)
            pages_scraped += 1
            print(f"✓ Scraped ({pages_scraped}/{max_pages}): {page_data['title']}")
            
            # Get all links from this page
            new_links = get_all_links(url)
            
            # Add new links to visit queue
            for link in new_links:
                if link not in visited_urls:
                    to_visit.add(link)
        
        # Be polite - don't overwhelm the server
        time.sleep(0.5)
    
    print("-" * 60)
    print(f"✅ Web scraping complete! Scraped {pages_scraped} pages.")
    return pages_scraped

def get_scraped_content_summary():
    """Get a summary of all scraped content for AI context"""
    try:
        conn = sqlite3.connect(config.DATABASE_NAME)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM scraped_content')
        count = cursor.fetchone()[0]
        
        if count == 0:
            conn.close()
            return "No website content has been scraped yet."
        
        # Get key pages
        cursor.execute('''
            SELECT title, content 
            FROM scraped_content 
            ORDER BY scraped_at DESC 
            LIMIT 10
        ''')
        
        pages = cursor.fetchall()
        conn.close()
        
        summary = f"Website content database contains {count} pages. Key information includes:\n\n"
        
        for title, content in pages:
            # Get first 500 characters of content
            preview = content[:500] + "..." if len(content) > 500 else content
            summary += f"Page: {title}\n{preview}\n\n"
        
        return summary
        
    except Exception as e:
        return f"Error retrieving scraped content: {str(e)}"

if __name__ == '__main__':
    # Run scraper
    scrape_website(max_pages=50)