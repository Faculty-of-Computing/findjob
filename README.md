# FindJob - Job Board Platform

A comprehensive web-based job board platform that connects job seekers with employers, built with Flask and SQLAlchemy.

## 📋 Overview

FindJob is designed to bridge the gap between qualified job seekers and employers looking for talent. The platform provides intuitive interfaces for posting jobs, searching opportunities, and managing applications with robust security and scalability features.

## ✨ Features

- **User Management**: Registration and authentication for job seekers, employers, and admins
- **Job Posting**: Employers can create and manage job listings
- **Job Search**: Advanced search and filtering capabilities
- **Application Tracking**: Seamless application submission and management
- **Admin Panel**: Comprehensive system management and reporting
- **File Uploads**: Secure resume and document uploads
- **Responsive Design**: Mobile-friendly interface
- **Real-time Notifications**: Email and in-app notifications

## 🛠 Tech Stack

- **Backend**: Flask 3.1.1
- **Database**: PostgreSQL (Supabase) / SQLAlchemy ORM
- **Frontend**: Jinja2 Templates, HTML5, CSS3, JavaScript
- **Authentication**: Flask-JWT, Werkzeug
- **Deployment**: Render, Gunicorn
- **Other**: Python-Dotenv, Flask-Session

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL database (or Supabase account)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Faculty-of-Computing/findjob.git
   cd findjob
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Database setup**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   flask run
   ```

Visit `http://localhost:5000` to access the application.
Visit  `https://findjob-bxs5.onrender.com` to access live site. 

## 📖 Usage

### For Job Seekers
- Register and create a profile
- Search and apply for jobs
- Track application status
- Upload resume and documents

### For Employers
- Post job openings
- Review and manage applications
- Access employer dashboard

### For Admins
- Manage users and jobs
- View reports and analytics
- System configuration

## 🌐 Deployment

FindJob is configured for easy deployment on Render with PostgreSQL.

### Production Deployment
1. Push code to GitHub
2. Connect repository to Render
3. Set environment variables in Render dashboard
4. Deploy automatically

See [Deployment Guide](docs/DEPLOYMENT_README.md) for detailed instructions.

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Introduction](docs/Introduction.md) - Project overview and objectives
- [System Design](docs/System_Design.md) - Architecture and technical details
- [Functional Requirements](docs/Functional_Requirements.md) - Feature specifications
- [API Documentation](docs/API_Documentation.md) - API endpoints and usage
- [User Manual](docs/User_Manual.md) - User guides and tutorials
- [UI/UX Documentation](docs/UI_UX_Documentation.md) - Interface design
- [Implementation Details](docs/Implementation_Details.md) - Code structure
- [Deployment Guide](docs/DEPLOYMENT_README.md) - Production setup
- [Risk and Mitigation](docs/Risk_and_Mitigation.md) - Security and risks
- [Software Process](docs/Software_Process.md) - Development methodology
- [System Documentation](docs/System_Documentation.md) - Complete system guide
- [Appendix](docs/Appendix.md) - Additional resources
- [Conclusion](docs/Conclusion.md) - Project summary

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Support

For support and questions:
- Check the [documentation](docs/)
- Open an issue on GitHub
- Contact the development team

## 🔄 Recent Updates

- Migrated to PostgreSQL with Supabase for better scalability
- Enhanced environment variable management with .env support
- Updated deployment configuration for production

---

**FindJob** - Connecting Talent with Opportunity</content>
<parameter name="filePath">/home/icekid/Projects/job-board/findjob/README.md
