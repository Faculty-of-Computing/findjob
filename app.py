#!/usr/bin/env python3

import os
import logging
from app import create_app

# Set up logging for production
if os.environ.get('FLASK_ENV') == 'production':
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

# Create the Flask application
try:
    app = create_app()
    logger.info("Flask app created successfully")
except Exception as e:
    logger.error(f"Failed to create Flask app: {e}")
    raise

if __name__ == '__main__':
    # Get environment variables with Render defaults
    host = '0.0.0.0'  # Bind to all interfaces
    port = int(os.environ.get('PORT', 5000))  # Render provides PORT environment variable
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'  # Default to False in production
    env = os.environ.get('FLASK_ENV', 'development')

    logger.info(f"Starting FindJob application...")
    logger.info(f"Environment: {env}")
    logger.info(f"Host: {host}, Port: {port}, Debug: {debug}")
    
    if env == 'production':
        logger.info(f"Production URL will be available on your Render domain")
    else:
        logger.info(f"Development URL: http://{host}:{port}")
    
    # Run the application
    # In production, use threaded=True for better performance
    app.run(
        host=host, 
        port=port, 
        debug=debug,
        threaded=True if env == 'production' else False
    )

# Export app for other WSGI servers if needed
application = app