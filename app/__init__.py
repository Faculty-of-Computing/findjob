from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from datetime import timedelta
import os

# Initialize SQLAlchemy instance globally
db = SQLAlchemy()

# Function to define app logic
def create_app():
    # Get the absolute path to the templates directory
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Configure the app for production/development
    if os.environ.get('FLASK_ENV') == 'production':
        # Production configuration
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///findjob.db')
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'bvaIbwm7Ctm2Gf2CZUUfaHU--qYbVUknAEwGcAcP_qs=')
        app.config['DEBUG'] = False
    else:
        # Development configuration
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///findjob.db'
        app.config['SECRET_KEY'] = 'bvaIbwm7Ctm2Gf2CZUUfaHU--qYbVUknAEwGcAcP_qs='
        app.config['DEBUG'] = True
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30) # After 30 days user login expires

    # Add custom Jinja2 filters to the app
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convert newlines to HTML line breaks"""
        if text is None:
            return ''
        return text.replace('\n', '<br>')

    # Initialize SQLAlchemy with the app
    db.init_app(app)
    
    # Import models after db is initialized (to avoid circular imports)
    from app.models import User, JobPosting, Application
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Create tables within app context
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    return app