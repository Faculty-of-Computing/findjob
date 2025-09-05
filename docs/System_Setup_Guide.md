# System Setup Guide

## Overview

This guide provides step-by-step instructions for developers to set up the FindJob application locally for development and testing purposes. The setup process covers all necessary components including Python environment, database, and application configuration.

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows (with WSL)
- **Python Version**: Python 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: Minimum 2GB free space
- **Network**: Internet connection for package installation

### Required Software
- **Python 3.8+**: Download from [python.org](https://python.org)
- **Git**: Version control system
- **Text Editor/IDE**: VS Code, PyCharm, or any preferred editor
- **Web Browser**: Chrome, Firefox, Safari, or Edge (latest version)

### Optional but Recommended
- **Virtual Environment**: `venv` (included with Python 3.3+) or `conda`
- **Database GUI**: DBeaver, phpMyAdmin, or similar for database management
- **API Testing Tool**: Postman or Insomnia for testing endpoints

## Installation Steps

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/Faculty-of-Computing/findjob.git

# Navigate to the project directory
cd findjob

# Verify the contents
ls -la
```

Expected output should show:
```
app.py
app/
create_admin.py
docs/
generate_secret.py
render.yaml
requirements.txt
static/
templates/
test_models.py
```

### Step 2: Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Verify activation (you should see (venv) in your prompt)
which python
```

### Step 3: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(Flask|SQLAlchemy|python-dotenv)"
```

Expected packages:
- Flask==3.1.1
- Flask-SQLAlchemy==3.1.1
- flask-cors==6.0.1
- python-dotenv==1.0.0
- PyJWT==2.3.0
- mysql-connector-python==9.1.0
- python-dateutil==2.8.2

### Step 4: Environment Configuration

#### Create Environment File

```bash
# Create .env file in the root directory
touch .env
```

Edit the `.env` file with the following content:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-development-secret-key-here

# Database Configuration (Development)
DATABASE_URL=sqlite:///findjob.db

# Email Configuration (Optional - for password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_USE_TLS=True

# File Upload Configuration
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# Security Configuration
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

#### Generate Secret Key

```bash
# Run the secret key generator
python generate_secret.py
```

Copy the generated secret key to your `.env` file.

### Step 5: Database Setup

#### Option A: SQLite (Recommended for Development)

```bash
# The application will automatically create the SQLite database
# when you run it for the first time
python app.py
```

#### Option B: MySQL (Production-like Setup)

```bash
# Install MySQL server (Ubuntu/Debian)
sudo apt update
sudo apt install mysql-server

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql

# Create database and user
sudo mysql -u root -p

# In MySQL shell:
CREATE DATABASE findjob;
CREATE USER 'findjob_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON findjob.* TO 'findjob_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Update .env file with MySQL configuration
DATABASE_URL=mysql://findjob_user:secure_password@localhost/findjob
```

### Step 6: Create Default Admin User

```bash
# Run the admin creation script
python create_admin.py

# Follow the prompts to create an admin user
```

### Step 7: Initialize Database

```bash
# The application will automatically create all tables
# when you run it for the first time
python app.py
```

You should see output like:
```
Database tables created successfully!
✅ DEFAULT ADMIN USER CREATED!
Username: admin
Email: admin@findjob.com
Password: admin123
⚠️  IMPORTANT: Change these credentials after first login!
```

## Running the Application

### Development Mode

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Run the application
python app.py
```

Expected output:
```
FindJob application...
Environment: development
Host: 0.0.0.0, Port: 5000, Debug: True
Development URL: http://0.0.0.0:5000
```

### Access the Application

Open your web browser and navigate to:
- **Local Development**: http://localhost:5000
- **Network Access**: http://0.0.0.0:5000 (accessible from other devices on the network)

### Production Mode

```bash
# Set production environment
export FLASK_ENV=production

# Run with production server
python app.py
```

## Testing the Setup

### Basic Functionality Tests

1. **Home Page**: Visit http://localhost:5000
2. **Registration**: Create a new user account
3. **Login**: Log in with the created account
4. **Job Posting**: Post a test job (employer role)
5. **Job Application**: Apply for a job (seeker role)

### Database Tests

```bash
# Check database connection
python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.models import User; print('Database connection successful')"

# Check table creation
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print(db.engine.table_names())"
```

### API Tests

```bash
# Test basic endpoints
curl http://localhost:5000/
curl http://localhost:5000/jobs
```

## Development Workflow

### Code Changes

```bash
# Make changes to the code
# The application will automatically reload in development mode

# Check for syntax errors
python -m py_compile app.py
python -m py_compile app/routes.py
python -m py_compile app/models.py
```

### Database Migrations

```bash
# If you make changes to models, you may need to recreate the database
rm findjob.db
python app.py
```

### Testing

```bash
# Run model tests
python test_models.py

# Run the application and manually test features
python app.py
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or run on different port
export PORT=5001
python app.py
```

#### 2. Database Connection Errors
```bash
# Check SQLite database
ls -la findjob.db

# Recreate database
rm findjob.db
python app.py
```

#### 3. Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print(sys.path)"
```

#### 4. Permission Errors
```bash
# Fix upload directory permissions
chmod 755 static/uploads
chmod 755 static/uploads/resumes
chmod 755 static/uploads/portfolios
```

#### 5. Virtual Environment Issues
```bash
# Deactivate and reactivate
deactivate
source venv/bin/activate

# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Debug Mode

Enable debug mode for detailed error information:

```bash
# In .env file
FLASK_ENV=development

# Or export
export FLASK_DEBUG=True
```

### Logging

Check application logs for errors:

```bash
# View recent logs
tail -f app.log

# Check for specific errors
grep "ERROR" app.log
```

## Advanced Configuration

### Environment Variables

Complete list of environment variables:

```env
# Flask Core
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=sqlite:///findjob.db

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=user@gmail.com
MAIL_PASSWORD=app-password
MAIL_USE_TLS=True

# File Upload
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216

# Security
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=2592000

# Server
HOST=0.0.0.0
PORT=5000
```

### Database Configuration

#### SQLite Configuration
- **File**: `findjob.db`
- **Location**: Project root directory
- **Backup**: Copy the `.db` file

#### MySQL Configuration
```env
DATABASE_URL=mysql://user:password@host:port/database
```

### Email Configuration

For password reset functionality:

1. **Gmail Setup**:
   - Enable 2-factor authentication
   - Generate app password
   - Use app password in configuration

2. **Other Providers**:
   - Update MAIL_SERVER and MAIL_PORT accordingly
   - Configure authentication as needed

## Deployment

### Local Production Test

```bash
# Test production configuration
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
python app.py
```

### Cloud Deployment

For production deployment to platforms like Render, Heroku, or AWS:

1. **Environment Variables**: Set all required environment variables
2. **Database**: Use production database (MySQL/PostgreSQL)
3. **Static Files**: Configure static file serving
4. **SSL**: Enable HTTPS
5. **Monitoring**: Set up logging and monitoring

## Getting Help

### Documentation
- **README.md**: Basic project information
- **docs/**: Comprehensive documentation
- **API_Documentation.md**: Endpoint specifications

### Support
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check docs/ folder for detailed guides
- **Code Comments**: Review inline code documentation

### Development Resources
- **Flask Documentation**: https://flask.palletsprojects.com/
- **SQLAlchemy Documentation**: https://sqlalchemy.org/
- **Python Documentation**: https://docs.python.org/3/

## Next Steps

After successful setup:

1. **Explore the Application**: Test all user roles and features
2. **Review Codebase**: Understand the application structure
3. **Run Tests**: Execute existing test suites
4. **Make Changes**: Start developing new features
5. **Contribute**: Submit pull requests for improvements

This setup guide ensures developers can quickly get the FindJob application running locally for development, testing, and contribution purposes.</content>