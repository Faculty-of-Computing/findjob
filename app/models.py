from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc, func, and_, or_
import json
from datetime import datetime, timedelta


class User(db.Model):
    """User model for both job seekers and employers"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='seeker')  # 'seeker', 'employer', 'admin'
    full_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Admin-specific fields
    permissions = db.Column(db.Text)  # JSON string for permissions
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Profile fields
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    
    # Relationships
    job_postings = db.relationship('JobPosting', backref='employer', lazy=True, foreign_keys='JobPosting.employer_id')
    applications = db.relationship('Application', backref='seeker', lazy=True, foreign_keys='Application.seeker_id')
    
    def __init__(self, username, email, password, role='seeker', full_name=None, phone=None, location=None, bio=None, created_by=None):
        """Initialize user with enhanced fields"""
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role
        self.full_name = full_name
        self.phone = phone
        self.location = location
        self.bio = bio
        self.created_by = created_by
        self.is_active = True
        self.created_at = datetime.utcnow()
        
        # Set default permissions based on role
        if role == 'admin':
            self.set_permissions(self.get_default_admin_permissions)
        else:
            self.permissions = '{}'

    def check_password(self, password):
        """Check if provided password matches the stored hash"""
        return check_password_hash(self.password, password)
    
    def set_password(self, password):
        """Set new password (hashed)"""
        self.password = generate_password_hash(password)
    
    def get_profile_data(self):
        """Get user profile data for display"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'phone': self.phone,
            'location': self.location,
            'bio': self.bio,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'role_display': 'Job Seeker' if self.role == 'seeker' else 'Employer' if self.role == 'employer' else 'Administrator'
        }
    
    def update_profile(self, username=None, email=None, new_password=None, 
                      full_name=None, phone=None, location=None, bio=None):
        """Update user profile information"""
        try:
            # Update basic fields
            if username is not None:
                self.username = username
            if email is not None:
                self.email = email
            if new_password is not None:
                self.set_password(new_password)
            
            # Update profile fields
            if full_name is not None:
                self.full_name = full_name if full_name.strip() else None
            if phone is not None:
                self.phone = phone if phone.strip() else None
            if location is not None:
                self.location = location if location.strip() else None
            if bio is not None:
                self.bio = bio if bio.strip() else None
            
            # Update timestamp
            self.updated_at = datetime.utcnow()
            
            # Commit changes
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating profile: {e}")
            return False
    
    def get_profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        fields = [
            self.username, self.email, self.full_name, 
            self.phone, self.location, self.bio
        ]
        completed_fields = sum(1 for field in fields if field and field.strip())
        return int((completed_fields / len(fields)) * 100)
    
    def to_dict(self):
        """Convert user object to dictionary (excluding password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name,
            'phone': self.phone,
            'location': self.location,
            'bio': self.bio,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_applied_jobs(self):
        """Get all jobs this seeker has applied for with real database data"""
        if self.role != 'seeker':
            return []
        
        try:
            # Query applications with job details using SQLAlchemy joins
            from sqlalchemy import desc
            
            applications = db.session.query(
                Application.id.label('application_id'),
                Application.application_date,
                Application.status,
                Application.cover_letter,
                JobPosting.id.label('job_id'),
                JobPosting.title.label('job_title'),
                JobPosting.company_name,
                JobPosting.location,
                JobPosting.job_type,
                JobPosting.salary_range,
                JobPosting.posted_date
            ).join(
                JobPosting, Application.job_id == JobPosting.id
            ).filter(
                Application.seeker_id == self.id
            ).order_by(
                desc(Application.application_date)
            ).all()
            
            # Convert to list of dictionaries for template use
            applied_jobs = []
            for app in applications:
                applied_jobs.append({
                    'application_id': app.application_id,
                    'job_id': app.job_id,
                    'job_title': app.job_title,
                    'company_name': app.company_name or 'Not specified',
                    'location': app.location or 'Not specified',
                    'job_type': app.job_type or 'Not specified',
                    'salary_range': app.salary_range,
                    'application_date': app.application_date,
                    'status': app.status,
                    'cover_letter': app.cover_letter,
                    'posted_date': app.posted_date
                })
            
            return applied_jobs
            
        except Exception as e:
            print(f"Error fetching applied jobs: {e}")
            return []
    
    # Get jobs posted by an employer
    def get_posted_jobs(self):
        """Get all jobs posted by this employer"""
        if self.role != 'employer':
            return []
        
        jobs = JobPosting.query.filter_by(employer_id=self.id).order_by(
            JobPosting.posted_date.desc()
        ).all()
        
        return [{
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'company_name': job.company_name,
            'location': job.location,
            'salary_range': job.salary_range,
            'job_type': job.job_type,
            'posted_date': job.posted_date,
            'is_active': job.is_active,
            'application_count': len(job.applications) if job.applications else 0,
            'view_count': 0  # Placeholder since we don't track views yet
        } for job in jobs]
    
    def get_recent_applications(self):
        """Get recent applications for employer's jobs"""
        if self.role != 'employer':
            return []
        
        # Get applications for this employer's jobs
        applications = db.session.query(Application).join(
            JobPosting, Application.job_id == JobPosting.id
        ).filter(
            JobPosting.employer_id == self.id
        ).order_by(Application.application_date.desc()).limit(10).all()  # Changed from applied_date to application_date

        return [{
            'application_id': app.id,
            'job_id': app.job_id,
            'job_title': app.job_posting.title,
            'applicant_name': app.seeker.username,
            'applicant_email': app.seeker.email,
            'application_date': app.application_date,
            'status': app.status,
            'cover_letter': app.cover_letter
        } for app in applications]
    
    @staticmethod
    def get_system_overview():
        """Get system overview statistics"""
        try:
            from app.models import JobPosting, Application
            
            total_users = User.query.count()
            total_jobs = JobPosting.query.count()
            total_applications = Application.query.count()
            
            # Get counts by role
            seekers_count = User.query.filter_by(role='seeker').count()
            employers_count = User.query.filter_by(role='employer').count()
            admins_count = User.query.filter_by(role='admin').count()
            
            # Get recent data (last 30 days)
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            recent_users = User.query.filter(User.created_at >= thirty_days_ago).all()
            recent_jobs = JobPosting.query.filter(JobPosting.posted_date >= thirty_days_ago).all()
            
            return {
                'total_users': total_users,
                'total_jobs': total_jobs,
                'total_applications': total_applications,
                'seekers_count': seekers_count,
                'employers_count': employers_count,
                'admins_count': admins_count,
                'recent_users': recent_users[:5],  # Last 5 users
                'recent_jobs': recent_jobs[:5],   # Last 5 jobs
                'new_users_this_month': len(recent_users),
                'new_jobs_this_month': len(recent_jobs),
                'new_applications_this_month': Application.query.filter(Application.application_date >= thirty_days_ago).count(),
                'total_employers': employers_count,
                'active_employers': employers_count,  # Simplified for now
                'applications_today': Application.query.filter(Application.application_date >= datetime.now().date()).count(),
                'jobs_posted_today': JobPosting.query.filter(JobPosting.posted_date >= datetime.now().date()).count(),
                'new_users_today': User.query.filter(User.created_at >= datetime.now().date()).count()
            }
        except Exception as e:
            print(f"Error in get_system_overview: {e}")
            return {
                'total_users': 0,
                'total_jobs': 0,
                'total_applications': 0,
                'seekers_count': 0,
                'employers_count': 0,
                'admins_count': 0,
                'recent_users': [],
                'recent_jobs': [],
                'new_users_this_month': 0,
                'new_jobs_this_month': 0,
                'new_applications_this_month': 0,
                'total_employers': 0,
                'active_employers': 0,
                'applications_today': 0,
                'jobs_posted_today': 0,
                'new_users_today': 0
            }
    
    @staticmethod
    def get_admin_count():
        """Get total number of admin users"""
        try:
            return User.query.filter_by(role='admin').count()
        except Exception as e:
            print(f"Error in get_admin_count: {e}")
            return 0
    
    @staticmethod
    def get_recent_admin_activities():
        """Get recent admin activities"""
        try:
            # For now, return recent admin logins or actions
            # You can expand this to track actual admin activities
            recent_admins = User.query.filter_by(role='admin').order_by(User.created_at.desc()).limit(5).all()
            
            activities = []
            for admin in recent_admins:
                activities.append({
                    'username': admin.username,
                    'action': 'Admin account created',
                    'date': admin.created_at
                })
            
            return activities
        except Exception as e:
            print(f"Error in get_recent_admin_activities: {e}")
            return []
    
    @staticmethod
    def get_active_users():
        """Get list of active users"""
        try:
            # Assuming you want all active users
            return User.query.all()
        except Exception as e:
            print(f"Error in get_active_users: {e}")
            return []
    
    def get_permissions(self):
        """Get user permissions"""
        if self.role == 'admin':
            return {
                'manage_users': True,
                'manage_jobs': True,
                'manage_applications': True,
                'view_reports': True,
                'system_settings': True
            }
        else:
            return {
                'manage_users': False,
                'manage_jobs': False,
                'manage_applications': False,
                'view_reports': False,
                'system_settings': False
            }

    def set_permissions(self, permissions_dict):
        """Set user permissions from dictionary"""
        import json
        if callable(permissions_dict):
            permissions_dict = permissions_dict()
        self.permissions = json.dumps(permissions_dict)

    def get_permissions(self):
        """Get user permissions as a dictionary"""
        if not self.permissions:
            if self.role == 'admin':
                return self.get_default_admin_permissions()
            return {}
    
        try:
            import json
            return json.loads(self.permissions)
        except:
            return {}

    def get_default_admin_permissions(self):
        """Get default admin permissions"""
        return {
            'can_manage_users': True,
            'can_manage_jobs': True,
            'can_view_analytics': True,
            'can_moderate_content': True
        }
    
    def get_role(self):
        """Get user role with validation"""
        return self.role.lower() if self.role else 'seeker'
    
    def is_valid_role(self):
        """Validate if user has a valid role"""
        valid_roles = ['seeker', 'employer', 'admin']
        return self.role and self.role.lower() in valid_roles
    
    @staticmethod
    def get_user_by_credentials(identifier):
        """Get user by username or email"""
        return User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

    @classmethod
    def create_admin(cls, username, email, password, permissions, full_name=None, created_by=None):
        """Create a new admin user with specified permissions"""
        try:
            from werkzeug.security import generate_password_hash
            import json
            
            # Create the admin user - remove created_at parameter
            new_admin = cls(
                username=username,
                email=email,
                password=generate_password_hash(password),
                role='admin',
                full_name=full_name
                # Remove created_at=datetime.utcnow() - this should be handled automatically
                # Remove created_by=created_by if your User model doesn't have this field
            )
            
            db.session.add(new_admin)
            db.session.flush()  # Get the ID without committing
            
            # Store permissions (assuming you have a permissions field or separate table)
            # If you have a permissions JSON field:
            new_admin.permissions = json.dumps(permissions)
            
            # Or if you handle permissions differently, adjust accordingly
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin: {e}")
            return False
        

class JobPosting(db.Model):
    """Enhanced JobPosting model with application requirements"""
    __tablename__ = 'job_postings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    company_name = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True, index=True)
    salary_range = db.Column(db.String(50), nullable=True)
    job_type = db.Column(db.String(20), default='full-time', nullable=True)  # Changed for SQLite
    posted_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_draft = db.Column(db.Boolean, default=False, nullable=False)
    draft_saved_at = db.Column(db.DateTime, nullable=True)
    published_at = db.Column(db.DateTime, nullable=True)
    
    # Application Requirements (what employer wants to collect)
    require_phone = db.Column(db.Boolean, default=True)
    require_address = db.Column(db.Boolean, default=False)
    require_work_authorization = db.Column(db.Boolean, default=True)
    require_experience_years = db.Column(db.Boolean, default=True)
    require_expected_salary = db.Column(db.Boolean, default=False)
    require_education = db.Column(db.Boolean, default=True)
    require_work_history = db.Column(db.Boolean, default=True)
    require_skills = db.Column(db.Boolean, default=True)
    require_portfolio = db.Column(db.Boolean, default=False)
    require_cover_letter = db.Column(db.Boolean, default=True)
    require_resume = db.Column(db.Boolean, default=True)  # Resume is typically always required
    require_portfolio_links = db.Column(db.Boolean, default=False)  # Portfolio links are optional by default
    
    # Custom questions for this job
    custom_questions = db.Column(db.Text, nullable=True)  # JSON string
    
    # Relationships
    applications = db.relationship('Application', backref='job_posting', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<JobPosting {self.title}>'
    
    @staticmethod
    def search_jobs(keyword):
        """Search for jobs by keyword in title or description"""
        if not keyword:
            return []
        
        # Use SQLite LIKE operator for case-insensitive search
        search_term = f"%{keyword}%"
        
        try:
            jobs = JobPosting.query.filter(
                db.and_(
                    JobPosting.is_active == True,
                    db.or_(
                        JobPosting.title.like(search_term),
                        JobPosting.description.like(search_term),
                        JobPosting.company_name.like(search_term),
                        JobPosting.location.like(search_term)
                    )
                )
            ).order_by(desc(JobPosting.date_posted)).all()
            
            return jobs
            
        except Exception as e:
            print(f"Search error: {e}")
            return []

class Application(db.Model):
    """Enhanced Application model for comprehensive job applications"""
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False, index=True)
    seeker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Basic application info
    application_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)
    
    # Personal Information
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    nationality = db.Column(db.String(50), nullable=True)
    work_authorization = db.Column(db.String(100), nullable=True)
    
    # Professional Profile
    years_experience = db.Column(db.Integer, nullable=True)
    expected_salary = db.Column(db.String(50), nullable=True)
    willing_to_relocate = db.Column(db.Boolean, default=False)
    willing_to_travel = db.Column(db.Boolean, default=False)
    
    # Education
    highest_qualification = db.Column(db.String(100), nullable=True)
    institution_name = db.Column(db.String(200), nullable=True)
    field_of_study = db.Column(db.String(100), nullable=True)
    graduation_year = db.Column(db.Integer, nullable=True)
    certifications = db.Column(db.Text, nullable=True)  # JSON string
    
    # Work Experience
    previous_employers = db.Column(db.Text, nullable=True)  # JSON string
    
    # Skills
    technical_skills = db.Column(db.Text, nullable=True)
    soft_skills = db.Column(db.Text, nullable=True)
    languages = db.Column(db.Text, nullable=True)  # JSON string
    
    # Documents and Links
    resume_filename = db.Column(db.String(200), nullable=True)
    cover_letter = db.Column(db.Text, nullable=True)
    portfolio_url = db.Column(db.String(200), nullable=True)
    linkedin_url = db.Column(db.String(200), nullable=True)
    github_url = db.Column(db.String(200), nullable=True)
    
    # Job-specific responses
    motivation = db.Column(db.Text, nullable=True)
    availability_date = db.Column(db.Date, nullable=True)
    referred_by = db.Column(db.String(100), nullable=True)
    custom_responses = db.Column(db.Text, nullable=True)  # JSON string for custom questions
    
    # Legal/Consent
    terms_accepted = db.Column(db.Boolean, default=False, nullable=False)
    data_consent = db.Column(db.Boolean, default=False, nullable=False)
    
    # Add unique constraint to prevent duplicate applications
    __table_args__ = (db.UniqueConstraint('job_id', 'seeker_id', name='unique_job_seeker_application'),)
    
    def __repr__(self):
        return f'<Application Job:{self.job_id} Seeker:{self.seeker_id}>'

# Helper function to create all tables
def create_tables(app):
    """Create all database tables"""
    with app.app_context():
        db.create_all()
        print("All database tables created successfully!")

# Helper function to drop all tables (for development/testing)
def drop_tables(app):
    """Drop all database tables"""
    with app.app_context():
        db.drop_all()
        print("All database tables dropped!")