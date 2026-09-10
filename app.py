"""
Express Credit Union AI Training Application
Main Flask Application File

This application helps train entry-level staff at Express Credit Union
by providing AI-powered answers to common questions about the company.

Author: Mustafa Al Hamowandi
"""

from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from openai import OpenAI
import config
from database import init_db, log_conversation, get_analytics_data, get_preset_questions, search_scraped_content
from datetime import datetime
import json
import requests

app = Flask(__name__)

# Initialize OpenAI client with Nvidia API
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=config.NVIDIA_API_KEY
)

# System prompt to guide the AI's behavior
SYSTEM_PROMPT = """You are an AI assistant for Express Credit Union in Seattle. Your role is to help train entry-level staff members by answering questions about the company.

You must be knowledgeable about these four main topics:

1. LOAN APPLICATIONS: 
   - First, ask if the applicant has a social security number (SSN)
   - If YES (they have SSN): Direct them to apply for a loan at: https://expresscu.myori.com/app/ola/ola-consumer-loan-type
   - If NO (they don't have SSN): They must FIRST apply for an ITIN (Individual Tax Identifier Number) at: https://www.expresscu.org/borrow/itin/
   - ITIN application requires proof of address
   - IMPORTANT: Include each URL only ONCE in your response. Do not repeat the same URL multiple times.

2. IMPROVING CREDIT SCORE:
   - Pay bills on time
   - Do an annual credit report to ensure information is correct
   - Schedule an appointment with a financial advisor/counselor at: https://www.expresscu.org/services/counseling/
   - Take small loans to show you can pay bills on time
   - Apply for a credit card
   - IMPORTANT: Include the counseling link when discussing credit score improvement

3. ACCOUNT TYPES AND SAVING MONEY:
   Express Credit Union offers several account types to help members save and manage their money:
   
   - Savings Account (Share/Savings): Become a member by opening a savings account. Benefits include no monthly maintenance fees (just $5 minimum balance), earning dividends (interest) paid quarterly, free online and mobile banking, and you become a credit union shareholder. Open with a deposit of $5 or more. More info: https://www.expresscu.org/bank/savings/
   
   - Certificate of Deposit (CD): Best for short-term or long-term savings goals. Benefits include fixed interest rates (you decide how much and how long to invest), higher returns than typical savings accounts, predictable returns, federally insured up to $250,000 by the NCUA, and directly supports the community. Existing members can call (206)-622-1850 or email socialimpactcd@expresscu.org. Non-members must establish membership first. More info: https://www.expresscu.org/bank/cd/
   
   - Social Impact CD: Make an impact in your community while you earn interest. This CD provides funds for Express CU to lend to low-income members and people who rely on overpriced, predatory finance companies. Smart investment for foundations, trusts, businesses, non-profits, and individuals. Your zero-risk, insured $50,000+ investment expands lending capacity and helps cover the cost of providing free accounts to unbanked and underbanked people in Washington State. Contact: socialimpactcd@expresscu.org or (206) 622-1850. More info: https://www.expresscu.org/bank/socialimpactCD/
   
   - Checking Account: For everyday transactions and bill payments. Benefits include no signup fees, no minimum balance requirements, zero monthly maintenance fees, access to unique loan products for members, rate discounts up to 1% by actively using your account, and access to competitive investment products. More info: https://www.expresscu.org/bank/checking/
   
   IMPORTANT: Include relevant account links when discussing savings options. Emphasize the benefits like no monthly fees, community support, and member advantages.

4. WHY USE EXPRESS CREDIT UNION:
   Express CU turns financial goals into fantastic realities by providing affordable and secure financial services to meet the diverse needs of WA State residents.
   
   Mission: Our mission is to collaborate with our community to create access to financial opportunities. Everyone deserves access to fair and affordable accounts and loans. Financially resilient families and households are the foundation for building strong societies.
   
   Vision: "Economic Justice for ALL" is our ultimate vision. We believe every individual deserves equal access to opportunity to be financially resilient and successful. We want to get to a place where our members aren't just surviving, but have the opportunity to thrive.
   
   Core Values:
   - Everyone deserves access to an affordable bank account regardless of income, credit, or immigration status
   - Express CU is a place where everyone can benefit
   - Secure alternative to banks, payday lenders, and check cashers
   - Providing accessible/flexible financial products helps people build credit, increase assets, and gain economic security
   - Help people become financially organized to meet their goals
   - Offer 'just in time' financial counseling, education, and personalized support to strengthen families and local communities
   
   Key Benefits:
   - Federally insured up to $250,000 by the NCUA - your money is protected
   - Fair to people no matter their class, including immigrants
   - Located in Seattle, serving Washington State residents
   - Community Development Financial Institution (CDFI) - awarded over $6 million in funding (2019-2023) to serve underserved communities
   - Unique products and services, second chance accounts, low fees and loan rates
   - Personalized service in members' primary language
   - Community partnerships to help members become financially resilient
   
   News & Updates: For the latest information, Annual Reports showing how we advance financial well-being for members and communities, and updates highlighting how the credit union continues to build a stronger, more inclusive financial future, visit: https://www.expresscu.org/about/news/
   
   IMPORTANT: Emphasize the credit union's mission of economic justice, accessibility for all regardless of immigration status or credit history, and commitment to helping people thrive, not just survive. Include the news link when discussing the organization's impact and progress.

You should answer these questions thoroughly and also handle follow-up questions. Be professional, friendly, and educational. Keep responses concise but informative. When providing links, mention each URL only once."""


@app.route('/')
def index():
    """Main chat interface page"""
    preset_questions = get_preset_questions()
    return render_template('index.html', preset_questions=preset_questions)


@app.route('/analytics')
def analytics():
    """Analytics dashboard page"""
    return render_template('analytics.html')


@app.route('/vin-decoder')
def vin_decoder():
    """VIN Decoder page"""
    return render_template('vin_decoder.html')


@app.route('/api/decode-vin', methods=['POST'])
def decode_vin():
    """Decode VIN using NHTSA API"""
    try:
        data = request.json
        vin = data.get('vin', '').strip().upper()
        
        if not vin:
            return jsonify({'error': 'No VIN provided'}), 400
        
        if len(vin) != 17:
            return jsonify({'error': 'VIN must be exactly 17 characters'}), 400
        
        # Call NHTSA VIN Decoder API
        api_url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
        
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        api_data = response.json()
        
        if 'Results' not in api_data:
            return jsonify({'error': 'Invalid response from VIN decoder'}), 500
        
        # Extract relevant information
        results = api_data['Results']
        
        # Helper function to find value by variable name
        def get_value(variable_name):
            for item in results:
                if item.get('Variable') == variable_name:
                    return item.get('Value') or 'N/A'
            return 'N/A'
        
        vehicle_info = {
            'VIN': vin,
            'ModelYear': get_value('Model Year'),
            'Make': get_value('Make'),
            'Model': get_value('Model'),
            'BodyClass': get_value('Body Class'),
            'EngineModel': get_value('Engine Model'),
            'Manufacturer': get_value('Manufacturer Name'),
            'VehicleType': get_value('Vehicle Type'),
            'ErrorText': get_value('Error Text') if get_value('Error Text') != 'N/A' else None
        }
        
        return jsonify(vehicle_info)
    
    except requests.RequestException as e:
        return jsonify({'error': f'Error connecting to VIN decoder service: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and stream AI responses"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        def generate():
            """Generator function for streaming responses"""
            full_response = ""
            
            try:
                print(f"Sending request to AI: {user_message}")  # Debug log
                
                # Search scraped content for relevant information
                relevant_content = search_scraped_content(user_message, limit=3)
                
                # Build enhanced system prompt with scraped content
                enhanced_prompt = SYSTEM_PROMPT
                
                if relevant_content:
                    enhanced_prompt += "\n\nADDITIONAL INFORMATION FROM WEBSITE:\n"
                    for i, content in enumerate(relevant_content, 1):
                        enhanced_prompt += f"\n{i}. {content['title']}\n"
                        enhanced_prompt += f"URL: {content['url']}\n"
                        enhanced_prompt += f"{content['content'][:500]}...\n"
                    enhanced_prompt += "\nUse this additional website information to provide more accurate and detailed answers.\n"
                
                # Call Nvidia API with streaming enabled
                stream = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": enhanced_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.2,
                    top_p=0.7,
                    max_tokens=1024,
                    stream=True  # Enable streaming
                )
                
                print("Streaming response started...")  # Debug log
                
                # Stream each chunk of the response
                for chunk in stream:
                    if not chunk.choices:
                        continue
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        
                        # Send each chunk as Server-Sent Event
                        yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"
                
                print(f"Streaming complete. Full response length: {len(full_response)}")  # Debug log
                
                # Send completion signal with timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                yield f"data: {json.dumps({'done': True, 'timestamp': timestamp})}\n\n"
                
                # Log complete conversation to database
                log_conversation(user_message, full_response)
                
            except Exception as e:
                print(f"Error in generate(): {str(e)}")  # Debug log
                import traceback
                traceback.print_exc()
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
    
    except Exception as e:
        print(f"Error in chat(): {str(e)}")  # Debug log
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data for the dashboard"""
    try:
        analytics_data = get_analytics_data()
        return jsonify(analytics_data)
    
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    # Check if scraping is needed
    import sqlite3
    conn = sqlite3.connect(config.DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT COUNT(*), MAX(scraped_at) FROM scraped_content')
        count, last_scraped = cursor.fetchone()
        conn.close()
        
        # Only scrape if database is empty or data is older than 7 days (1 week)
        needs_scraping = False
        
        if count == 0:
            print("\n📋 No scraped data found. Running initial scrape...")
            needs_scraping = True
        elif last_scraped:
            from datetime import datetime, timedelta
            last_date = datetime.strptime(last_scraped, '%Y-%m-%d %H:%M:%S')
            days_old = (datetime.now() - last_date).days
            
            if datetime.now() - last_date > timedelta(days=7):
                print(f"\n🔄 Data is {days_old} days old. Updating...")
                needs_scraping = True
            else:
                print(f"\n✅ Using existing scraped data ({count} pages, last updated {days_old} days ago)")
        
        if needs_scraping:
            print("="*60)
            print("SCRAPING EXPRESS CREDIT UNION WEBSITE")
            print("="*60)
            
            try:
                from webscraper import scrape_website
                pages_scraped = scrape_website(max_pages=10)
                print(f"\n✅ Successfully scraped {pages_scraped} pages from the website!")
            except Exception as e:
                print(f"\n⚠️  Warning: Web scraping failed: {str(e)}")
                print("The app will continue with existing information.")
            
            print("="*60 + "\n")
            
    except sqlite3.OperationalError:
        # Table doesn't exist yet, scrape for first time
        conn.close()
        print("\n📋 First time setup - scraping website...")
        print("="*60)
        print("SCRAPING EXPRESS CREDIT UNION WEBSITE")
        print("="*60)
        
        try:
            from webscraper import scrape_website
            pages_scraped = scrape_website(max_pages=10)
            print(f"\n✅ Successfully scraped {pages_scraped} pages!")
        except Exception as e:
            print(f"\n⚠️  Warning: Web scraping failed: {str(e)}")
        
        print("="*60 + "\n")
    
    # Run Flask app
    print("Starting Express Credit Union AI Training Application...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, port=5000)