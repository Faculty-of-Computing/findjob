from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import db, User, JobPosting, Application
from werkzeug.security import check_password_hash
from datetime import datetime
import json

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
    """Homepage route - displays welcome message and overview"""
    # Auto-redirect logged-in users to their dashboard
    dashboard_redirect = validate_session_and_redirect()
    if dashboard_redirect:
        return dashboard_redirect
    
    # Show homepage for non-logged-in users
    return render_template('home.html')

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
        
        # Basic validation
        if not title:
            flash('Job title is required.', 'error')
            return render_template('post_job.html')
        
        if not description:
            flash('Job description is required.', 'error')
            return render_template('post_job.html')
        
        if len(title) > 200:
            flash('Job title must be 200 characters or less.', 'error')
            return render_template('post_job.html')
        
        try:
            # Create new job posting
            new_job = JobPosting(
                title=title,
                description=description,
                employer_id=session['user_id'],
                company_name=company_name if company_name else None,
                location=location if location else None,
                salary_range=salary_range if salary_range else None,
                job_type=job_type
            )
            
            db.session.add(new_job)
            db.session.commit()
            
            flash(f'Job "{title}" posted successfully!', 'success')
            return redirect(url_for('main.jobs'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while posting the job. Please try again.', 'error')
            return render_template('post_job.html')
    
    return render_template('post_job.html')

@main.route('/apply_job/<int:job_id>', methods=['POST'])
def apply_job(job_id):
    """Job application route - allows seekers to apply for jobs"""
    # Check if user is logged in
    if not is_logged_in():
        flash('Please log in to apply for jobs.', 'error')
        return redirect(url_for('main.login'))
    
    # Check if user is a seeker
    if session.get('user_role') != 'seeker':
        flash('Only job seekers can apply for jobs. Please register as a job seeker.', 'error')
        return redirect(url_for('main.jobs'))
    
    # Check if job exists and is active
    job = JobPosting.query.filter_by(id=job_id, is_active=True).first()
    if not job:
        flash('Job not found or no longer active.', 'error')
        return redirect(url_for('main.jobs'))
    
    # Check if user already applied for this job
    existing_application = Application.query.filter_by(
        job_id=job_id, 
        seeker_id=session['user_id']
    ).first()
    
    if existing_application:
        flash('You have already applied for this job.', 'info')
        return redirect(url_for('main.jobs'))
    
    # Get cover letter from form (optional)
    cover_letter = request.form.get('cover_letter', '').strip()
    
    try:
        # Create new application
        new_application = Application(
            job_id=job_id,
            seeker_id=session['user_id'],
            cover_letter=cover_letter if cover_letter else None
        )
        
        db.session.add(new_application)
        db.session.commit()
        
        flash(f'Successfully applied for "{job.title}"!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while submitting your application. Please try again.', 'error')
    
    return redirect(url_for('main.jobs'))

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
    """User profile view - displays current user's profile information"""
    # Check if user is logged in
    if not is_logged_in():
        flash('Please log in to access your profile.', 'error')
        return redirect(url_for('main.login'))
    
    # Get current user
    current_user = get_current_user()
    if not current_user:
        flash('User session expired. Please log in again.', 'error')
        return redirect(url_for('main.login'))
    
    try:
        # Get additional profile data
        profile_data = current_user.get_profile_data()
        
        # Calculate profile statistics
        if current_user.role == 'seeker':
            applied_jobs_count = len(current_user.get_applied_jobs())
            profile_stats = {
                'applications_submitted': applied_jobs_count,
                'account_age_days': (datetime.utcnow() - current_user.created_at).days
            }
        elif current_user.role == 'employer':
            posted_jobs = current_user.get_posted_jobs()
            total_applications = sum(job.get('application_count', 0) for job in posted_jobs)
            profile_stats = {
                'jobs_posted': len(posted_jobs),
                'total_applications_received': total_applications,
                'account_age_days': (datetime.utcnow() - current_user.created_at).days
            }
        else:
            profile_stats = {
                'account_age_days': (datetime.utcnow() - current_user.created_at).days
            }
        
        return render_template('profile.html', 
                             user=current_user,
                             profile_data=profile_data,
                             profile_stats=profile_stats)
                             
    except Exception as e:
        flash('Error loading profile data. Please try again.', 'error')
        return redirect(url_for('main.home'))

@main.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """Edit user profile - allows users to update their profile information"""
    # Check if user is logged in
    if not is_logged_in():
        flash('Please log in to edit your profile.', 'error')
        return redirect(url_for('main.login'))
    
    # Get current user
    current_user = get_current_user()
    if not current_user:
        flash('User session expired. Please log in again.', 'error')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        # Get form data
        new_username = request.form.get('username', '').strip()
        new_email = request.form.get('email', '').strip()
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()
        bio = request.form.get('bio', '').strip()
        
        # Basic validation
        if not new_username:
            flash('Username is required.', 'error')
            return render_template('edit_profile.html', user=current_user)
        
        if not new_email:
            flash('Email is required.', 'error')
            return render_template('edit_profile.html', user=current_user)
        
        if len(new_username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return render_template('edit_profile.html', user=current_user)
        
        if len(new_username) > 80:
            flash('Username must be 80 characters or less.', 'error')
            return render_template('edit_profile.html', user=current_user)
        
        # Email format validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, new_email):
            flash('Please enter a valid email address.', 'error')
            return render_template('edit_profile.html', user=current_user)
        
        # Password validation (if user wants to change password)
        if new_password:
            if not current_password:
                flash('Current password is required to change password.', 'error')
                return render_template('edit_profile.html', user=current_user)
            
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'error')
                return render_template('edit_profile.html', user=current_user)
            
            if len(new_password) < 6:
                flash('New password must be at least 6 characters long.', 'error')
                return render_template('edit_profile.html', user=current_user)
            
            if new_password != confirm_password:
                flash('New password and confirmation do not match.', 'error')
                return render_template('edit_profile.html', user=current_user)
        
        try:
            # Check for username uniqueness (excluding current user)
            if new_username != current_user.username:
                existing_user = User.query.filter_by(username=new_username).first()
                if existing_user:
                    flash('Username already exists. Please choose a different username.', 'error')
                    return render_template('edit_profile.html', user=current_user)
            
            # Check for email uniqueness (excluding current user)
            if new_email != current_user.email:
                existing_email = User.query.filter_by(email=new_email).first()
                if existing_email:
                    flash('Email already exists. Please use a different email address.', 'error')
                    return render_template('edit_profile.html', user=current_user)
            
            # Update user profile
            update_success = current_user.update_profile(
                username=new_username,
                email=new_email,
                new_password=new_password if new_password else None,
                full_name=full_name if full_name else None,
                phone=phone if phone else None,
                location=location if location else None,
                bio=bio if bio else None
            )
            
            if update_success:
                # Update session data if username changed
                if new_username != session.get('username'):
                    session['username'] = new_username
                
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('main.profile'))
            else:
                flash('Failed to update profile. Please try again.', 'error')
                return render_template('edit_profile.html', user=current_user)
                
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile. Please try again.', 'error')
            return render_template('edit_profile.html', user=current_user)
    
    # GET request - display edit form
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

# Utility function to check if user is logged in
def is_logged_in():
    """Check if user is currently logged in"""
    return 'user_id' in session

# Utility function to get current user
def get_current_user():
    """Get current logged-in user object"""
    if is_logged_in():
        return User.query.get(session['user_id'])
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