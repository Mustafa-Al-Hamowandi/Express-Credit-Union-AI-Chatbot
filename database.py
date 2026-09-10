"""
Database functions for Express Credit Union AI Training Application

This module handles all SQLite database operations including:
- Creating tables
- Logging conversations
- Retrieving analytics data
"""

import sqlite3
from datetime import datetime
import config

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(config.DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            question_category TEXT
        )
    ''')
    
    # Create preset_questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preset_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL,
            category TEXT NOT NULL,
            display_order INTEGER
        )
    ''')
    
    # Check if preset questions already exist
    cursor.execute('SELECT COUNT(*) FROM preset_questions')
    count = cursor.fetchone()[0]
    
    # Insert preset questions if table is empty
    if count == 0:
        preset_questions = [
            ("I never applied for a loan. How can I apply?", "Loan Application", 1),
            ("How do I improve my credit score?", "Credit Score", 2),
            ("What kind of accounts do you offer, and how do I save money?", "Account Types", 3),
            ("Why should I use Express Credit Union when I can save money at home?", "Benefits", 4)
        ]
        
        cursor.executemany(
            'INSERT INTO preset_questions (question_text, category, display_order) VALUES (?, ?, ?)',
            preset_questions
        )
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")


def log_conversation(user_message, ai_response):
    """
    Log a conversation to the database
    
    Args:
        user_message: The user's question
        ai_response: The AI's response
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Determine question category based on keywords
    category = categorize_question(user_message)
    
    cursor.execute(
        '''INSERT INTO conversations (user_message, ai_response, question_category) 
           VALUES (?, ?, ?)''',
        (user_message, ai_response, category)
    )
    
    conn.commit()
    conn.close()


def categorize_question(question):
    """
    Categorize a question based on keywords
    
    Args:
        question: The user's question text
        
    Returns:
        Category string
    """
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['loan', 'apply', 'application', 'itin', 'ssn']):
        return "Loan Application"
    elif any(word in question_lower for word in ['credit score', 'improve', 'credit report']):
        return "Credit Score"
    elif any(word in question_lower for word in ['account', 'save', 'saving', 'cd', 'ira', 'retirement']):
        return "Account Types"
    elif any(word in question_lower for word in ['why', 'benefit', 'insurance', 'protection', 'home']):
        return "Benefits"
    else:
        return "Other"


def get_preset_questions():
    """
    Get all preset questions from the database
    
    Returns:
        List of dictionaries containing question data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT id, question_text, category FROM preset_questions ORDER BY display_order'
    )
    
    questions = []
    for row in cursor.fetchall():
        questions.append({
            'id': row['id'],
            'text': row['question_text'],
            'category': row['category']
        })
    
    conn.close()
    return questions


def get_analytics_data():
    """
    Get analytics data for the dashboard
    
    Returns:
        Dictionary containing analytics information
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total conversations
    cursor.execute('SELECT COUNT(*) as total FROM conversations')
    total_conversations = cursor.fetchone()['total']
    
    # Questions by category
    cursor.execute('''
        SELECT question_category, COUNT(*) as count 
        FROM conversations 
        GROUP BY question_category 
        ORDER BY count DESC
    ''')
    category_counts = []
    for row in cursor.fetchall():
        category_counts.append({
            'category': row['question_category'],
            'count': row['count']
        })
    
    # Recent conversations - NOW INCLUDING AI RESPONSES
    cursor.execute('''
        SELECT timestamp, user_message, ai_response, question_category 
        FROM conversations 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''')
    recent_conversations = []
    for row in cursor.fetchall():
        recent_conversations.append({
            'timestamp': row['timestamp'],
            'message': row['user_message'],
            'response': row['ai_response'],
            'category': row['question_category']
        })
    
    conn.close()
    
    return {
        'total_conversations': total_conversations,
        'category_counts': category_counts,
        'recent_conversations': recent_conversations
    }


def search_scraped_content(query, limit=5):
    """
    Search scraped website content for relevant information
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        
    Returns:
        List of relevant content snippets
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Search for pages containing query keywords
        search_terms = query.lower().split()
        
        cursor.execute('''
            SELECT title, content, url 
            FROM scraped_content 
            WHERE LOWER(content) LIKE ? OR LOWER(title) LIKE ?
            ORDER BY scraped_at DESC
            LIMIT ?
        ''', (f'%{search_terms[0]}%', f'%{search_terms[0]}%', limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'title': row['title'],
                'content': row['content'][:1000],  # First 1000 chars
                'url': row['url']
            })
        
        conn.close()
        return results
        
    except Exception as e:
        print(f"Error searching scraped content: {str(e)}")
        return []