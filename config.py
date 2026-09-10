"""
Configuration file for Express Credit Union AI Training Application

IMPORTANT: This file reads your Nvidia API key from a .env file.
Create a .env file in this same folder (see .env.example) and add:
    NVIDIA_API_KEY=your_real_key_here
Never commit the .env file to git.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # reads variables from .env into the environment

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")

if not NVIDIA_API_KEY:
    raise ValueError(
        "NVIDIA_API_KEY not found. Create a .env file with NVIDIA_API_KEY=your_key"
    )

# Database configuration
DATABASE_NAME = "express_cu.db"

# Flask configuration
DEBUG_MODE = True
PORT = 5000