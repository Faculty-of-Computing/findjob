from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import db, User, JobPosting, Application
from werkzeug.security import check_password_hash
from datetime import datetime
import json
from sqlalchemy import func

# Create a blueprint for main routes
main = Blueprint('main', __name__)

def redirect_to_user_dashboard(user_role):
    """Helper function to redirect users to appropriate dashboard based on role"""
    try:
        dashboard_routes = {
            'seeker': 'main.seeker_dashboard',
            'employer': 'main.employer_dashboard',
            'admin': 'main.admin_dashboard'
        }
        
        route = dashboard_routes.get(user_role)
        if route:
            return redirect(url_for(route))
        else:
            flash('Invalid user role. Please contact support.', 'error')
            return redirect(url_for('main.home'))
            
    except Exception as e:
        flash('Dashboard access error. Please try again.', 'warning')
        return redirect(url_for('main.home'))

def validate_session_and_redirect():
    """Validate user session and redirect to appropriate dashboard if logged in"""
    if is_logged_in():
        user_role = session.get('user_role')
        if user_role:
            return redirect_to_user_dashboard(user_role)
    return None

# Update the home route to handle auto-redirect for logged-in users
@main.route('/')
def home():
    """Home page with statistics"""
    try:
        stats = User.get_system_overview()
        return render_template('home.html', 
                             total_users=stats['total_users'],
                             total_jobs=stats['total_jobs'],
                             total_applications=stats['total_applications'])
    except Exception as e:
        print(f"Error getting home statistics: {e}")
        return render_template('home.html', 
                             total_users=0,
                             total_jobs=0,
                             total_applications=0)

@main.route('/jobs')
def jobs():
    """Job listings route - displays all active job postings"""
    # Get all active job postings, ordered by most recent
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of jobs per page
    
    jobs = JobPosting.query.filter_by(is_active=True)\
                          .order_by(JobPosting.posted_date.desc())\
                          .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('jobs.html', jobs=jobs)

@main.route('/post_job', methods=['GET', 'POST'])
def post_job():
    """Job posting route - allows employers to create new job postings"""
    # Check if user is logged in
    if not is_logged_in():
        flash('Please log in to post a job.', 'error')
        return redirect(url_for('main.login'))
    
    # Check if user is an employer
    if session.get('user_role') != 'employer':
        flash('Only employers can post jobs. Please register as an employer.', 'error')
        return redirect(url_for('main.jobs'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        company_name = request.form.get('company_name', '').strip()
        location = request.form.get('location', '').strip()
        salary_range = request.form.get('salary_range', '').strip()
        job_type = request.form.get('job_type', 'full-time')
        
        # Application requirements
        require_phone = bool(request.form.get('require_phone'))
        require_address = bool(request.form.get('require_address'))
        require_work_authorization = bool(request.form.get('require_work_authorization'))
        require_experience_years = bool(request.form.get('require_experience_years'))
        require_expected_salary = bool(request.form.get('require_expected_salary'))
        require_education = bool(request.form.get('require_education'))
        require_skills = bool(request.form.get('require_skills'))
        require_cover_letter = bool(request.form.get('require_cover_letter'))
        require_resume = bool(request.form.get('require_resume'))
        require_portfolio_links = bool(request.form.get('require_portfolio_links'))
        
        # Determine if saving as draft or publishing
        is_active = bool(request.form.get('is_active'))
        is_draft = not is_active
        
        # Basic validation - always required even for drafts
        if not title:
            flash('Job title is required.', 'error')
            return render_template('post_job.html')
        
        # For publishing, require all mandatory fields
        if not is_draft:
            if not description:
                flash('Job description is required for publishing.', 'error')
                return render_template('post_job.html')
            
            if not company_name:
                flash('Company name is required for publishing.', 'error')
                return render_template('post_job.html')
            
            if not location:
                flash('Location is required for publishing.', 'error')
                return render_template('post_job.html')
        
        try:
            # Create new job posting
            new_job = JobPosting(
                title=title,
                description=description,
                company_name=company_name,
                location=location,
                salary_range=salary_range if salary_range else None,
                job_type=job_type,
                employer_id=session['user_id'],
                require_phone=require_phone,
                require_address=require_address,
                require_work_authorization=require_work_authorization,
                require_experience_years=require_experience_years,
                require_expected_salary=require_expected_salary,
                require_education=require_education,
                require_skills=require_skills,
                require_cover_letter=require_cover_letter,
                require_resume=require_resume,
                require_portfolio_links=require_portfolio_links,
                is_active=is_active,
                is_draft=is_draft,
                draft_saved_at=datetime.utcnow(),
                published_at=datetime.utcnow() if is_active else None
            )
            
            db.session.add(new_job)
            db.session.commit()
            
            if is_active:
                flash('Job posted successfully and is now live!', 'success')
            else:
                flash('Job saved as draft successfully! You can publish it later from your dashboard.', 'success')
            return redirect(url_for('main.employer_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error saving job: {e}")  # Log the actual error
            flash('An error occurred while saving the job. Please try again.', 'error')
            return render_template('post_job.html')
    
    return render_template('post_job.html')

@main.route('/apply/<int:job_id>')
def apply_job_form(job_id):
    """Display application form for a specific job"""
    if not is_logged_in():
        flash('Please log in to apply for jobs.', 'error')
        return redirect(url_for('main.login'))
    
    if session.get('user_role') != 'seeker':
        flash('Only job seekers can apply for jobs.', 'error')
        return redirect(url_for('main.jobs'))
    
    job = JobPosting.query.filter_by(id=job_id, is_active=True).first()
    if not job:
        flash('Job not found or no longer active.', 'error')
        return redirect(url_for('main.jobs'))
    
    # Check if already applied
    existing_application = Application.query.filter_by(
        job_id=job_id, seeker_id=session['user_id']
    ).first()
    
    if existing_application:
        flash('You have already applied for this job.', 'info')
        return redirect(url_for('main.jobs'))
    
    current_user = get_current_user()
    return render_template('apply_job.html', job=job, user=current_user)

@main.route('/submit_application/<int:job_id>', methods=['POST'])
def submit_application(job_id):
    """Process application submission"""
    if not is_logged_in():
        flash('Please log in to apply for jobs.', 'error')
        return redirect(url_for('main.login'))
    
    if session.get('user_role') != 'seeker':
        flash('Only job seekers can apply for jobs.', 'error')
        return redirect(url_for('main.jobs'))
    
    job = JobPosting.query.filter_by(id=job_id, is_active=True).first()
    if not job:
        flash('Job not found or no longer active.', 'error')
        return redirect(url_for('main.jobs'))
    
    # Check if already applied
    existing_application = Application.query.filter_by(
        job_id=job_id, seeker_id=session['user_id']
    ).first()
    
    if existing_application:
        flash('You have already applied for this job.', 'info')
        return redirect(url_for('main.jobs'))
    
    try:
        # Handle file upload
        resume_filename = None
        if 'resume' in request.files:
            resume = request.files['resume']
            if resume.filename:
                # Create uploads directory if it doesn't exist
                import os
                upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save file with unique name
                import uuid
                file_extension = resume.filename.rsplit('.', 1)[1].lower()
                resume_filename = f"{uuid.uuid4()}.{file_extension}"
                resume.save(os.path.join(upload_dir, resume_filename))
        
        # Create application with all the data
        new_application = Application(
            job_id=job_id,
            seeker_id=session['user_id'],
            
            # Personal Information
            full_name=request.form.get('full_name', '').strip(),
            email=request.form.get('email', '').strip(),
            phone=request.form.get('phone', '').strip(),
            address=request.form.get('address', '').strip(),
            work_authorization=request.form.get('work_authorization', '').strip(),
            
            # Professional Profile
            years_experience=int(request.form.get('years_experience', 0)) if request.form.get('years_experience') else None,
            expected_salary=request.form.get('expected_salary', '').strip(),
            willing_to_relocate=bool(request.form.get('willing_to_relocate')),
            willing_to_travel=bool(request.form.get('willing_to_travel')),
            
            # Education
            highest_qualification=request.form.get('highest_qualification', '').strip(),
            institution_name=request.form.get('institution_name', '').strip(),
            field_of_study=request.form.get('field_of_study', '').strip(),
            graduation_year=int(request.form.get('graduation_year', 0)) if request.form.get('graduation_year') else None,
            certifications=request.form.get('certifications', '').strip(),
            
            # Skills
            technical_skills=request.form.get('technical_skills', '').strip(),
            soft_skills=request.form.get('soft_skills', '').strip(),
            languages=request.form.get('languages', '').strip(),
            
            # Documents and Links
            resume_filename=resume_filename,
            cover_letter=request.form.get('cover_letter', '').strip(),
            portfolio_url=request.form.get('portfolio_url', '').strip(),
            linkedin_url=request.form.get('linkedin_url', '').strip(),
            github_url=request.form.get('github_url', '').strip(),
            
            # Job-specific
            motivation=request.form.get('motivation', '').strip(),
            availability_date=datetime.strptime(request.form.get('availability_date'), '%Y-%m-%d').date() if request.form.get('availability_date') else None,
            referred_by=request.form.get('referred_by', '').strip(),
            
            # Legal
            terms_accepted=bool(request.form.get('terms_accepted')),
            data_consent=bool(request.form.get('data_consent'))
        )
        
        db.session.add(new_application)
        db.session.commit()
        
        flash(f'Successfully applied for "{job.title}"! Your application has been submitted.', 'success')
        return redirect(url_for('main.seeker_dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while submitting your application. Please try again.', 'error')
        print(f"Application error: {e}")
        return redirect(url_for('main.apply_job_form', job_id=job_id))

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Login route - handles user authentication with automatic dashboard redirection"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        remember_me = request.form.get('remember_me') == 'on'
        
        print(f"Login attempt - Email: {email}, Password length: {len(password) if password else 0}")
        
        # Validate input
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('login.html')
        
        try:
            # Find user by email (simplified approach)
            user = User.query.filter_by(email=email).first()
            print(f"User found: {user is not None}")
            
            if user:
                print(f"User role: {user.role}")
                password_match = check_password_hash(user.password, password)
                print(f"Password match: {password_match}")
                
                if password_match:
                    # Store user information in session
                    session['user_id'] = user.id
                    session['username'] = user.username
                    session['user_role'] = user.role
                    session['user_email'] = user.email
                    
                    # Set session permanent if remember me is checked
                    if remember_me:
                        session.permanent = True
                    
                    # Update last login (optional - only if column exists)
                    try:
                        user.last_login = datetime.now()
                        db.session.commit()
                    except Exception as e:
                        print(f"Could not update last_login: {e}")
                        # Continue without updating last_login
                    
                    flash(f'Welcome back, {user.username}!', 'success')
                    
                    # Role-based dashboard redirection
                    try:
                        if user.role == 'seeker':
                            return redirect(url_for('main.seeker_dashboard'))
                        elif user.role == 'employer':
                            return redirect(url_for('main.employer_dashboard'))
                        elif user.role == 'admin':
                            return redirect(url_for('main.admin_dashboard'))
                        else:
                            # Handle unknown role
                            flash('Unknown user role detected. Please contact support.', 'warning')
                            return redirect(url_for('main.home'))
                            
                    except Exception as redirect_error:
                        print(f"Redirection error: {redirect_error}")
                        # Handle redirection errors
                        flash('Dashboard access error. Redirecting to home page.', 'warning')
                        return redirect(url_for('main.home'))
                else:
                    flash('Invalid email or password. Please try again.', 'error')
                    return render_template('login.html')
            else:
                flash('Invalid email or password. Please try again.', 'error')
                return render_template('login.html')
                
        except Exception as e:
            print(f"Login exception: {e}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            flash('Login error occurred. Please try again.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    """Registration route - handles user registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        terms = request.form.get('terms')
        
        # Validate form data
        if not all([username, email, password, confirm_password, role, terms]):
            flash('Please fill in all required fields and accept the terms.', 'error')
            return render_template('register.html')
        
        # Check password confirmation
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return render_template('register.html')
        
        # Validate password length
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        # Validate role
        if role not in ['seeker', 'employer']:
            flash('Please select a valid role.', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                flash('Username already exists. Please choose a different one.', 'error')
            else:
                flash('Email already registered. Please use a different email.', 'error')
            return render_template('register.html')
        
        try:
            # Create new user
            new_user = User(username=username, email=email, password=password, role=role)
            db.session.add(new_user)
            db.session.commit()
            
            # Auto-login after successful registration
            session['user_id'] = new_user.id
            session['user_role'] = new_user.role
            session['username'] = new_user.username
            
            flash(f'Account created successfully! Welcome to Job Board, {username}!', 'success')
            
            # Redirect to appropriate dashboard based on user role
            return redirect_to_user_dashboard(new_user.role)
                
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@main.route('/logout')
def logout():
    """Logout route - clears user session"""
    username = session.get('username', 'User')
    session.clear()
    flash(f'You have been logged out successfully. Goodbye, {username}!', 'info')
    return redirect(url_for('main.home'))

@main.route('/about')
def about():
    """About route - displays information about the job board"""
    return render_template('about.html')

@main.route('/seeker_dashboard')
def seeker_dashboard():
    """Job seeker dashboard - displays applied jobs and application status"""
    # Check if user is logged in
    if not is_logged_in():
        flash('Please log in to access your dashboard.', 'error')
        return redirect(url_for('main.login'))
    
    # Check if user is a seeker
    if session.get('user_role') != 'seeker':
        flash('Access denied. This dashboard is for job seekers only.', 'error')
        return redirect(url_for('main.home'))
    
    # Get current user
    current_user = get_current_user()
    if not current_user:
        flash('User session expired. Please log in again.', 'error')
        return redirect(url_for('main.login'))
    
    try:
        # Get applied jobs with real data from database
        applied_jobs = current_user.get_applied_jobs()
        
        # Calculate statistics
        total_applications = len(applied_jobs)
        pending_count = len([app for app in applied_jobs if app.get('status') == 'pending'])
        reviewed_count = len([app for app in applied_jobs if app.get('status') == 'reviewed'])
        accepted_count = len([app for app in applied_jobs if app.get('status') == 'accepted'])
        rejected_count = len([app for app in applied_jobs if app.get('status') == 'rejected'])
        
        return render_template('seeker_dashboard.html', 
                             applied_jobs=applied_jobs,
                             user=current_user,
                             total_applications=total_applications,
                             pending_count=pending_count,
                             reviewed_count=reviewed_count,
                             accepted_count=accepted_count,
                             rejected_count=rejected_count)
                             
    except Exception as e:
        flash('Error loading dashboard data. Please try again.', 'error')
        return redirect(url_for('main.home'))

@main.route('/employer_dashboard')
def employer_dashboard():
    """Employer dashboard - displays posted jobs and received applications"""
    # Check if user is logged in
    if not is_logged_in():
        flash('Please log in to access your dashboard.', 'error')
        return redirect(url_for('main.login'))
    
    # Check if user is an employer
    if session.get('user_role') != 'employer':
        flash('Access denied. This dashboard is for employers only.', 'error')
        return redirect(url_for('main.home'))
    
    # Get current user
    current_user = get_current_user()
    if not current_user:
        flash('User session expired. Please log in again.', 'error')
        return redirect(url_for('main.login'))
    
    try:
        # Get posted jobs and applications with real data from database
        posted_jobs = current_user.get_posted_jobs()
        
        # Get recent applications
        recent_applications = current_user.get_recent_applications()
        
        # Calculate statistics
        total_jobs = len(posted_jobs)
        active_jobs = len([job for job in posted_jobs if job.get('is_active', True)])
        total_applications = sum(job.get('application_count', 0) for job in posted_jobs)
        pending_applications = len([app for app in recent_applications if app.get('status') == 'pending'])
        total_views = sum(job.get('view_count', 0) for job in posted_jobs)
        
        return render_template('employer_dashboard.html',
                             posted_jobs=posted_jobs,
                             recent_applications=recent_applications,
                             user=current_user,
                             total_jobs=total_jobs,
                             active_jobs=active_jobs,
                             total_applications=total_applications,
                             pending_applications=pending_applications,
                             total_views=total_views)
                             
    except Exception as e:
        print(f"Employer dashboard error: {e}")
        flash('Error loading dashboard data. Please try again.', 'error')
        return redirect(url_for('main.home'))

@main.route('/admin')
@main.route('/admin_dashboard')
def admin_dashboard():
    """Admin dashboard - displays system overview and management options"""
    # Check if user is logged in
    if not is_logged_in():
        flash('Please log in to access the admin dashboard.', 'error')
        return redirect(url_for('main.login'))
    
    # Check if user is an admin
    if session.get('user_role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.home'))
    
    # Get current user and check permissions
    current_user = get_current_user()
    if not current_user:
        flash('User session expired. Please log in again.', 'error')
        return redirect(url_for('main.login'))
    
    try:
        # Get system overview with real data from database
        system_stats = User.get_system_overview()
        
        # Get admin-specific data
        admin_data = {
            'total_admins': User.get_admin_count(),
            'recent_admin_activities': User.get_recent_admin_activities(),
            'system_health': {
                'database_status': 'Connected',
                'last_backup': 'Not configured',
                'active_sessions': len([u for u in User.get_active_users() if u.get('is_active')])
            }
        }
        
        return render_template('admin.html',
                             stats=system_stats,
                             admin_data=admin_data,
                             user=current_user,
                             user_permissions=current_user.get_permissions())
                             
    except Exception as e:
        flash('Error loading admin dashboard data. Please try again.', 'error')
        return redirect(url_for('main.home'))

@main.route('/admin/create_admin', methods=['GET', 'POST'])
def create_admin():
    """Create new admin - allows existing admins to create new administrators"""
    # Check if user is logged in
    if not is_logged_in():
        flash('Please log in to access admin creation.', 'error')
        return redirect(url_for('main.login'))
    
    # Check if user is an admin
    if session.get('user_role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.home'))
    
    # Get current user and check permissions
    current_user = get_current_user()
    if not current_user:
        flash('User session expired. Please log in again.', 'error')
        return redirect(url_for('main.login'))
    
    # Check if user has permission to manage users
    user_permissions = current_user.get_permissions()
    if not user_permissions.get('manage_users', False):
        flash('Access denied. You do not have permission to create admins.', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        
        # Get permissions from checkboxes
        permissions = {
            'manage_users': 'manage_users' in request.form,
            'manage_jobs': 'manage_jobs' in request.form,
            'manage_applications': 'manage_applications' in request.form,
            'view_reports': 'view_reports' in request.form,
            'system_settings': 'system_settings' in request.form
        }
        
        # Basic validation
        if not username:
            flash('Username is required.', 'error')
            return render_template('create_admin.html', user=current_user)
        
        if not email:
            flash('Email is required.', 'error')
            return render_template('create_admin.html', user=current_user)
        
        if not password:
            flash('Password is required.', 'error')
            return render_template('create_admin.html', user=current_user)
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return render_template('create_admin.html', user=current_user)
        
        if len(username) > 80:
            flash('Username must be 80 characters or less.', 'error')
            return render_template('create_admin.html', user=current_user)
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('create_admin.html', user=current_user)
        
        if password != confirm_password:
            flash('Password and confirmation do not match.', 'error')
            return render_template('create_admin.html', user=current_user)
        
        # Email format validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('Please enter a valid email address.', 'error')
            return render_template('create_admin.html', user=current_user)
        
        # Check for at least one permission
        if not any(permissions.values()):
            flash('Please assign at least one permission to the new admin.', 'error')
            return render_template('create_admin.html', user=current_user)
        
        try:
            # Check for existing username and email
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists. Please choose a different username.', 'error')
                return render_template('create_admin.html', user=current_user)
            
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('Email already exists. Please use a different email address.', 'error')
                return render_template('create_admin.html', user=current_user)
            
            # Create new admin user
            success = User.create_admin(
                username=username,
                email=email,
                password=password,
                permissions=permissions,
                full_name=full_name if full_name else None,
                created_by=current_user.id
            )
            
            if success:
                flash(f'Admin "{username}" created successfully with assigned permissions!', 'success')
                return redirect(url_for('main.admin_dashboard'))
            else:
                flash('Failed to create admin. Please try again.', 'error')
                return render_template('create_admin.html', user=current_user)
                
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the admin. Please try again.', 'error')
            return render_template('create_admin.html', user=current_user)
    
    # GET request - display create admin form
    return render_template('create_admin.html', user=current_user)

@main.route('/admin/manage_users')
def manage_users():
    """Manage users - view and edit user accounts"""
    # Check authentication and permissions
    if not is_logged_in():
        flash('Please log in to access user management.', 'error')
        return redirect(url_for('main.login'))
    
    if session.get('user_role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.home'))
    
    current_user = get_current_user()
    if not current_user:
        flash('User session expired. Please log in again.', 'error')
        return redirect(url_for('main.login'))
    
    # Check permission
    user_permissions = current_user.get_permissions()
    if not user_permissions.get('manage_users', False):
        flash('Access denied. You do not have permission to manage users.', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
    try:
        # Get all users for management
        users = User.get_all_users_for_admin()
        
        return render_template('manage_users.html',
                             users=users,
                             user=current_user)
                             
    except Exception as e:
        flash('Error loading user data. Please try again.', 'error')
        return redirect(url_for('main.admin_dashboard'))

@main.route('/profile')
def profile():
    """User profile page - view profile information"""
    if not is_logged_in():
        flash('Please log in to view your profile.', 'error')
        return redirect(url_for('main.login'))
    
    current_user = get_current_user()
    if not current_user:
        flash('User session expired. Please log in again.', 'error')
        return redirect(url_for('main.login'))
    
    # Get additional profile data
    profile_data = {
        'phone': current_user.phone,
        'location': current_user.location,
        'bio': current_user.bio
    }
    
    # Calculate profile statistics
    profile_stats = {
        'applications_submitted': 0,  # You'll need to implement this based on your database
        'jobs_posted': 0,  # You'll need to implement this based on your database  
        'total_applications_received': 0,  # You'll need to implement this based on your database
        'account_age_days': (datetime.now() - current_user.created_at).days if current_user.created_at else 0
    }
    
    return render_template('profile.html', 
                         user=current_user, 
                         profile_data=profile_data, 
                         profile_stats=profile_stats)

@main.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """Edit user profile"""
    if not is_logged_in():
        flash('Please log in to edit your profile.', 'error')
        return redirect(url_for('main.login'))
    
    current_user = get_current_user()
    if not current_user:
        flash('User session expired. Please log in again.', 'error')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        # Update profile fields
        current_user.full_name = request.form.get('full_name', '').strip()
        current_user.phone = request.form.get('phone', '').strip()
        current_user.location = request.form.get('location', '').strip()
        current_user.bio = request.form.get('bio', '').strip()
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'error')
    
    return render_template('edit_profile.html', user=current_user)

@main.route('/search', methods=['GET', 'POST'])
def search():
    """Job search route - allows users to search for jobs by keyword"""
    query = request.args.get('q', '').strip()
    jobs = []
    
    if query:
        try:
            # Get search results from the model
            jobs = JobPosting.search_jobs(query)
            flash(f'Found {len(jobs)} job(s) matching "{query}"', 'info')
        except Exception as e:
            flash('An error occurred while searching. Please try again.', 'error')
            jobs = []
    
    return render_template('jobs.html', jobs=jobs, search_query=query, is_search=True)

@main.route('/dashboard')
def get_user_dashboard():
    """Redirect users to their appropriate dashboard based on role"""
    if not is_logged_in():
        flash('Please log in to access your dashboard.', 'error')
        return redirect(url_for('main.login'))
    
    user_role = session.get('user_role')
    if user_role == 'employer':
        return redirect(url_for('main.employer_dashboard'))
    elif user_role == 'seeker':
        return redirect(url_for('main.seeker_dashboard'))
    elif user_role == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    else:
        return redirect(url_for('main.home'))

# Utility function to check if user is logged in
def is_logged_in():
    """Check if user is currently logged in"""
    return 'user_id' in session

# Utility function to get current user
def get_current_user():
    """Get current logged-in user object"""
    if is_logged_in():
        user_id = session.get('user_id')
        return User.query.get(user_id)
    return None

# Make utility functions available in templates
@main.app_template_global()
def current_user():
    """Template global function to get current user"""
    return get_current_user()

@main.app_template_global()
def logged_in():
    """Template global function to check login status"""
    return is_logged_in()

# Error handlers
@main.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404

@main.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('errors/500.html'), 500

@main.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    """Edit job posting (for drafts or published jobs)"""
    if not is_logged_in():
        flash('Please log in to edit jobs.', 'error')
        return redirect(url_for('main.login'))
    
    if session.get('user_role') != 'employer':
        flash('Only employers can edit jobs.', 'error')
        return redirect(url_for('main.jobs'))
    
    job = JobPosting.query.filter_by(id=job_id, employer_id=session['user_id']).first()
    if not job:
        flash('Job not found or you do not have permission to edit it.', 'error')
        return redirect(url_for('main.employer_dashboard'))
    
    if request.method == 'POST':
        # Update job details
        job.title = request.form.get('title', '').strip()
        job.description = request.form.get('description', '').strip()
        job.company_name = request.form.get('company_name', '').strip()
        job.location = request.form.get('location', '').strip()
        job.salary_range = request.form.get('salary_range', '').strip()
        job.job_type = request.form.get('job_type', 'full-time')
        
        # Update requirements
        job.require_phone = bool(request.form.get('require_phone'))
        job.require_address = bool(request.form.get('require_address'))
        job.require_work_authorization = bool(request.form.get('require_work_authorization'))
        job.require_experience_years = bool(request.form.get('require_experience_years'))
        job.require_expected_salary = bool(request.form.get('require_expected_salary'))
        job.require_education = bool(request.form.get('require_education'))
        job.require_skills = bool(request.form.get('require_skills'))
        job.require_cover_letter = bool(request.form.get('require_cover_letter'))
        job.require_resume = bool(request.form.get('require_resume'))
        job.require_portfolio_links = bool(request.form.get('require_portfolio_links'))
        
        # Handle publishing/draft status
        is_active = bool(request.form.get('is_active'))
        was_draft = job.is_draft
        
        job.is_active = is_active
        job.is_draft = not is_active
        job.draft_saved_at = datetime.utcnow()
        
        # If publishing for the first time, set published_at
        if is_active and was_draft:
            job.published_at = datetime.utcnow()
        
        # Validation for publishing
        if not job.is_draft:
            if not job.title:
                flash('Job title is required for publishing.', 'error')
                return render_template('edit_job.html', job=job)
            
            if not job.description:
                flash('Job description is required for publishing.', 'error')
                return render_template('edit_job.html', job=job)
            
            if not job.company_name:
                flash('Company name is required for publishing.', 'error')
                return render_template('edit_job.html', job=job)
            
            if not job.location:
                flash('Location is required for publishing.', 'error')
                return render_template('edit_job.html', job=job)
        
        try:
            db.session.commit()
            
            if is_active and was_draft:
                flash('Job published successfully!', 'success')
            elif is_active:
                flash('Job updated successfully!', 'success')
            else:
                flash('Job saved as draft successfully!', 'success')
            
            return redirect(url_for('main.employer_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the job. Please try again.', 'error')
    
    return render_template('edit_job.html', job=job)

@main.route('/publish_job/<int:job_id>', methods=['POST'])
def publish_job(job_id):
    """Publish a draft job"""
    if not is_logged_in():
        flash('Please log in to publish jobs.', 'error')
        return redirect(url_for('main.login'))
    
    if session.get('user_role') != 'employer':
        flash('Only employers can publish jobs.', 'error')
        return redirect(url_for('main.jobs'))
    
    job = JobPosting.query.filter_by(id=job_id, employer_id=session['user_id'], is_draft=True).first()
    if not job:
        flash('Draft job not found.', 'error')
        return redirect(url_for('main.employer_dashboard'))
    
    # Validate required fields before publishing
    if not job.title or not job.description or not job.company_name or not job.location:
        flash('Please complete all required fields before publishing.', 'error')
        return redirect(url_for('main.edit_job', job_id=job_id))
    
    try:
        job.is_active = True
        job.is_draft = False
        job.published_at = datetime.utcnow()
        
        db.session.commit()
        flash('Job published successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while publishing the job.', 'error')
    
    return redirect(url_for('main.employer_dashboard'))

@main.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    """Delete a job posting"""
    if not is_logged_in():
        flash('Please log in to delete jobs.', 'error')
        return redirect(url_for('main.login'))
    
    if session.get('user_role') != 'employer':
        flash('Only employers can delete jobs.', 'error')
        return redirect(url_for('main.jobs'))
    
    job = JobPosting.query.filter_by(id=job_id, employer_id=session['user_id']).first()
    if not job:
        flash('Job not found.', 'error')
        return redirect(url_for('main.employer_dashboard'))
    
    try:
        db.session.delete(job)
        db.session.commit()
        flash('Job deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the job.', 'error')
    
    return redirect(url_for('main.employer_dashboard'))