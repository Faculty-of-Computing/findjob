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
        db_path = os.path.join(os.path.dirname(__file__), '..', 'findjob.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SECRET_KEY'] = 'bvaIbwm7Ctm2Gf2CZUUfaHU--qYbVUknAEwGcAcP_qs='
        app.config['DEBUG'] = True
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

    # Add custom Jinja2 filters to the app
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convert newlines to HTML line breaks"""
        if text:
            return text.replace('\n', '<br>')
        return text

    # Initialize SQLAlchemy with the app
    db.init_app(app)
    
    # Import models after db is initialized (to avoid circular imports)
    from app.models import User, JobPosting, Application
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Create tables and ensure admin user exists within app context
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
        
        # Create default admin user if none exists
        create_default_admin()
    
    # Ensure uploads directory exists
    uploads_dir = os.path.join(app.static_folder, 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    
    return app

def create_default_admin():
    """Create a default admin user if no admin exists"""
    try:
        from app.models import User
        
        # Check if any admin user exists
        admin_exists = User.query.filter_by(role='admin').first()
        
        if not admin_exists:
            # Create default admin user
            admin_user = User(
                username='admin',
                email='admin@findjob.com',
                password='admin123',  # This will be hashed by the User model
                role='admin',
            )
            
            # Set default admin permissions if your User model supports it
            if hasattr(admin_user, 'set_permissions'):
                admin_user.set_permissions({
                    'manage_users': True,
                    'manage_jobs': True,
                    'manage_applications': True,
                    'view_reports': True,
                    'system_settings': True
                })
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("=" * 50)
            print("✅ DEFAULT ADMIN USER CREATED!")
            print("Username: admin")
            print("Email: admin@jobhub.com")
            print("Password: admin123")
            print("⚠️  IMPORTANT: Change these credentials after first login!")
            print("=" * 50)
            
        else:
            print("✅ Admin user already exists in the system.")
            
    except Exception as e:
        print(f"❌ Error creating default admin user: {e}")
        db.session.rollback()