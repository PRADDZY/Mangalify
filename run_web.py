#!/usr/bin/env python3
"""
Standalone script to run the Mangalify web dashboard
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required environment variables
required_vars = ['MONGO_URI', 'WEB_ADMIN_PASSWORD']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print("Error: Missing required environment variables:")
    for var in missing_vars:
        print(f"  - {var}")
    print("\nPlease set these variables in your .env file")
    sys.exit(1)

# Import and run the Flask app
from web.app import app

if __name__ == '__main__':
    port = int(os.getenv('WEB_PORT', 5000))
    host = os.getenv('WEB_HOST', '0.0.0.0')
    debug = os.getenv('WEB_DEBUG', 'False').lower() == 'true'
    
    print("=" * 60)
    print("🎉 Mangalify Web Dashboard")
    print("=" * 60)
    print(f"\nStarting web server on http://{host}:{port}")
    print(f"Debug mode: {debug}")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60)
    
    app.run(host=host, port=port, debug=debug)
