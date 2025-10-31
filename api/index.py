"""
XMRT-DAO-Ecosystem API Entry Point for Vercel
This file wraps the Flask app for Vercel's Python WSGI runtime
"""

import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables for Vercel serverless environment
os.environ.setdefault('MESH_PORT', 'simulate')
os.environ.setdefault('MESH_UPDATE_INTERVAL', '30')
os.environ.setdefault('FLASK_ENV', 'production')

# Import the Flask app from the root app.py
from app import app

# Export for Vercel's WSGI runtime
# Flask apps are WSGI applications and Vercel handles them correctly
