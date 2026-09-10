# Express Credit Union AI Training Application

An AI-powered training application for Express Credit Union staff members in Seattle. This application helps entry-level employees learn about the company's services, policies, and procedures through an interactive chat interface.

**Author:** Mustafa Al Hamowandi  
**Course Project:** Python Web Application Development  
**Client:** Express Credit Union, Seattle

---

## Features

- **Interactive Chat Interface**: Staff can ask questions and receive AI-powered responses
- **Preset Questions**: Four main questions that cover essential company information
- **Free-form Chat**: Staff can ask follow-up questions or type custom queries
- **Analytics Dashboard**: View usage statistics and most frequently asked questions
- **SQLite Database**: Stores conversation history and analytics data
- **Plotly Visualization**: Bar chart showing question frequency by category

---

## Prerequisites

Before running this application, make sure you have:

1. **Python 3.8 or higher** installed on your Windows system
2. **Nvidia API Key** (you should already have this)
3. **Visual Studio Code** (already installed)

---

## Installation Instructions

### Step 1: Create Project Directory

1. Open Visual Studio Code
2. Create a new folder for your project (e.g., `express_cu_ai`)
3. Open this folder in VS Code

### Step 2: Create Project Structure

Create the following folders and files in your project directory:
```
express_cu_ai/
├── app.py
├── config.py
├── database.py
├── templates/
│   ├── index.html
│   └── analytics.html
├── static/
│   └── style.css
└── README.md
```

### Step 3: Install Required Libraries

Open the terminal in VS Code (Terminal → New Terminal) and run:
```bash
pip install flask openai plotly
```

### Step 4: Configure Your API Key

1. Install python-dotenv if you haven't already: `pip install python-dotenv`
2. Create a file named `.env` in the project root (same folder as `config.py`)
3. Add your Nvidia API key to it:


**IMPORTANT:** Keep this file secure and never share it publicly!

---

## How to Run the Application

### Step 1: Start the Application

In the VS Code terminal, navigate to your project folder and run:
```bash
python app.py
```

You should see output like:
```
Database initialized successfully!
Starting Express Credit Union AI Training Application...
Open your browser and go to: http://localhost:5000
 * Running on http://127.0.0.1:5000
```

### Step 2: Open in Browser

1. Open your web browser (Chrome, Firefox, Edge, etc.)
2. Go to: `http://localhost:5000`
3. You should see the Express Credit Union AI Training interface

### Step 3: Stop the Application

To stop the application:
- In the VS Code terminal, press `Ctrl + C`

---

## Using the Application

### Main Chat Interface (`/`)

1. **Quick Questions**: Click any of the four preset question buttons to instantly ask that question
2. **Free-form Chat**: Type your own question in the text box and click "Send" (or press Enter)
3. **Follow-up Questions**: Continue the conversation by asking related questions

### Analytics Dashboard (`/analytics`)

1. Click "Analytics" in the navigation menu
2. View statistics:
   - Total number of conversations
   - Most popular question category
   - Bar chart of questions by category
   - Recent conversation history

---

## Database Information

The application uses SQLite with parameterized queries (SQL injection prevention).

### Tables:

1. **conversations**: Stores all chat interactions
   - `id`: Primary key
   - `timestamp`: When the conversation occurred
   - `user_message`: The question asked
   - `ai_response`: The AI's answer
   - `question_category`: Category of the question

2. **preset_questions**: Stores the four main questions
   - `id`: Primary key
   - `question_text`: The question text
   - `category`: Question category
   - `display_order`: Order to display questions

### Database File

The database is automatically created as `express_cu.db` in your project folder when you first run the application.

---

## The Four Main Questions

The AI is trained to answer these questions about Express Credit Union:

1. **Loan Applications**: How to apply for a loan (SSN/ITIN requirements)
   - Asks if applicant has social security number
   - If no SSN, directs to ITIN (Individual Tax Identifier Number) application
   - ITIN application requires proof of address

2. **Credit Score Improvement**: Tips for improving credit scores
   - Pay bills on time
   - Do annual credit report to ensure information is correct
   - Schedule appointment with financial advisor if needed
   - Take small loans to show you can pay bills on time
   - Apply for a credit card

3. **Account Types**: Basic accounts, IRA, and Certificate of Deposit (CD)
   - Basic account
   - Individual Retirement Account (IRA)
   - Certificate of Deposit (CD)

4. **Why Choose Express CU**: Benefits of banking with Express Credit Union
   - Protects money from theft
   - Insurance coverage of up to $250,000
   - Mission: Offer everyone access to banking
   - Fair to people no matter their class, including immigrants
   - Located in Seattle

---

## Troubleshooting

### Error: "No module named 'flask'"
- Run: `pip install flask openai plotly`

### Error: "API key not found" or "Invalid API key"
- Check that you've added your Nvidia API key to `config.py`
- Make sure there are no extra spaces or quotes

### Port 5000 already in use
- Edit `config.py` and change `PORT = 5000` to another port (e.g., `PORT = 5001`)
- Then go to `http://localhost:5001` in your browser

### Database errors
- Delete `express_cu.db` and restart the application (it will recreate the database)

### Can't connect to Nvidia API
- Check your internet connection
- Verify your API key is valid
- Check if the Nvidia API service is operational

---

## Project Requirements Checklist

✅ **SQLite Database**: Uses SQLite with two tables  
✅ **SQL Injection Prevention**: Uses parameterized queries (`?` placeholders)  
✅ **Two GUI Screens**: Chat interface and Analytics dashboard  
✅ **Matplotlib/Plotly Graph**: Bar chart showing question frequency  
✅ **Real-world Client**: Express Credit Union, Seattle  
✅ **Python Code Only**: All files are `.py`, `.html`, `.css`  
✅ **README File**: Complete setup and usage instructions

---

## Technology Stack

- **Backend**: Python 3, Flask web framework
- **Database**: SQLite3 with parameterized queries
- **AI Integration**: Nvidia API with OpenAI library (Llama 3.3 70B model)
- **Frontend**: HTML5, CSS3, JavaScript
- **Visualization**: Plotly.js for interactive bar charts
- **Styling**: Custom CSS with responsive design

---

## File Descriptions

- **app.py**: Main Flask application with routes and AI integration
- **config.py**: Configuration file with API key and settings
- **database.py**: Database functions and SQL queries with parameterized statements
- **templates/index.html**: Chat interface HTML (Screen 1)
- **templates/analytics.html**: Analytics dashboard HTML (Screen 2)
- **static/style.css**: Styling for the web application
- **README.md**: This file - setup and usage instructions
- **express_cu.db**: SQLite database file (auto-generated on first run)

---

## Security Notes

- Never commit the `.env` file to version control (e.g., GitHub) — it's already excluded via `.gitignore`
- `config.py` no longer contains the key directly; it reads from `.env` at runtime
- The API key should be kept confidential
- All database queries use parameterized statements to prevent SQL injection
- This application is for educational/training purposes
- Consider adding authentication for production use

---

## Future Enhancements

Potential improvements for future versions:
- User authentication and role-based access
- Export conversation history to CSV
- Email notifications for staff training completion
- Multi-language support for diverse communities
- Mobile app version
- Voice input/output capabilities

---

## Support

For questions about this project:
- Review the code comments in each file
- Check the troubleshooting section above
- Refer to Flask documentation: https://flask.palletsprojects.com/
- Refer to OpenAI library documentation: https://github.com/openai/openai-python
- Refer to Plotly documentation: https://plotly.com/python/

---

## Acknowledgments

- **Express Credit Union** for providing the opportunity to work on this real-world project
- **Nvidia** for providing AI API access
- **Python & Flask Community** for excellent documentation and resources

---

## License

This is a class project for Express Credit Union. All rights reserved.

---

**Project completed: November 2024**