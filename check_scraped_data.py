"""
Check what data has been scraped from the website
"""

import sqlite3
import config

def check_scraped_data():
    """Display all scraped pages"""
    conn = sqlite3.connect(config.DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get count
    cursor.execute('SELECT COUNT(*) FROM scraped_content')
    count = cursor.fetchone()[0]
    
    print(f"\n📊 Total pages scraped: {count}\n")
    print("="*80)
    
    # Get all pages
    cursor.execute('SELECT url, title, LENGTH(content) as content_length FROM scraped_content')
    
    for i, row in enumerate(cursor.fetchall(), 1):
        url, title, length = row
        print(f"{i}. {title}")
        print(f"   URL: {url}")
        print(f"   Content Length: {length} characters")
        print("-"*80)
    
    conn.close()

if __name__ == '__main__':
    check_scraped_data()