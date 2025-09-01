#!/usr/bin/env python3

import os
from app import create_app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Get environment variables with Render defaults
    host = '0.0.0.0'  # Bind to all interfaces
    port = int(os.environ.get('PORT', 5000))  # Render provides PORT environment variable
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'  # Default to False in production

    print(f"Starting FindJob application...")
    print(f"Visit: http://{host}:{port}")
    
    # Run the application
    app.run(host=host, port=port, debug=debug)