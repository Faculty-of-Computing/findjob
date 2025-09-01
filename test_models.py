#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, User, JobPosting, Application

def test_models():
    """Test the database models"""
    app = create_app()
    
    with app.app_context():
        try:
            # Test User creation
            print("Testing User model...")
            employer = User(username='testemployer', email='employer@test.com', 
                           password='password123', role='employer')
            seeker = User(username='testseeker', email='seeker@test.com', 
                         password='password123', role='seeker')
            
            db.session.add(employer)
            db.session.add(seeker)
            db.session.commit()
            print("✅ User models created successfully")
            
            # Test JobPosting creation
            print("Testing JobPosting model...")
            job = JobPosting(title='Test Developer Position',
                           description='A test job posting for developers',
                           employer_id=employer.id,
                           company_name='Test Company',
                           location='Remote',
                           job_type='full-time')
            
            db.session.add(job)
            db.session.commit()
            print("✅ JobPosting model created successfully")
            
            # Test Application creation
            print("Testing Application model...")
            application = Application(job_id=job.id, seeker_id=seeker.id,
                                    cover_letter='I am very interested in this position.')
            
            db.session.add(application)
            db.session.commit()
            print("✅ Application model created successfully")
            
            # Test relationships
            print("Testing model relationships...")
            print(f"Employer {employer.username} has {len(employer.job_postings)} job postings")
            print(f"Job '{job.title}' has {len(job.applications)} applications")
            print(f"Seeker {seeker.username} has {len(seeker.applications)} applications")
            
            # Test model methods
            print("Testing model methods...")
            print(f"Job posting dictionary: {job.to_dict()}")
            print(f"Password check for employer: {employer.check_password('password123')}")
            
            print("✅ All model tests passed!")
            
        except Exception as e:
            print(f"❌ Model test failed: {e}")
            
        finally:
            # Clean up test data
            db.session.rollback()

if __name__ == "__main__":
    test_models()