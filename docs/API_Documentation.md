# API Documentation

FindJob uses a traditional web application architecture with server-side rendered pages rather than a pure REST API. However, the application exposes several key endpoints that can be considered part of its API surface.

## Base URL
```
Development: http://localhost:5000
Production: https://your-render-domain.com
```

## Authentication

### Session-based Authentication
FindJob uses Flask sessions for user authentication. Users must be logged in to access protected routes.

#### Login Process
- **Endpoint**: `POST /login`
- **Method**: POST
- **Content-Type**: `application/x-www-form-urlencoded`

**Request Body**:
```
username=john_doe&password=secure_password
```

**Response**: Redirect to dashboard or error page

#### Logout Process
- **Endpoint**: `GET /logout`
- **Method**: GET
- **Authentication**: Required (active session)

**Response**: Redirect to home page with session cleared

## Core Endpoints

### 1. Home Page
- **Endpoint**: `GET /`
- **Method**: GET
- **Authentication**: Optional
- **Description**: Displays system statistics and featured jobs

**Response**: HTML page with statistics

### 2. Job Listings
- **Endpoint**: `GET /jobs`
- **Method**: GET
- **Authentication**: Optional
- **Query Parameters**:
  - `page` (integer): Page number for pagination (default: 1)
  - `search` (string): Search keyword for job filtering

**Response**: HTML page with paginated job listings

### 3. Job Details
- **Endpoint**: `GET /apply/<int:job_id>`
- **Method**: GET
- **Authentication**: Optional
- **Path Parameters**:
  - `job_id` (integer): Unique identifier for the job posting

**Response**: HTML page with detailed job information and application form

### 4. Job Application Submission
- **Endpoint**: `POST /submit_application/<int:job_id>`
- **Method**: POST
- **Authentication**: Required (job seeker role)
- **Content-Type**: `multipart/form-data`
- **Path Parameters**:
  - `job_id` (integer): Job posting identifier

**Request Body** (multipart/form-data):
```
full_name=John Doe
email=john@example.com
phone=+1234567890
resume_file=<uploaded_file>
cover_letter=<text>
# ... other application fields
```

**Response**: Redirect to dashboard with success/error message

### 5. User Registration
- **Endpoint**: `POST /register`
- **Method**: POST
- **Authentication**: None required
- **Content-Type**: `application/x-www-form-urlencoded`

**Request Body**:
```
username=john_doe
email=john@example.com
password=secure_password
confirm_password=secure_password
role=seeker
full_name=John Doe
```

**Response**: Redirect to login page or error page

### 6. Job Posting
- **Endpoint**: `POST /post_job`
- **Method**: POST
- **Authentication**: Required (employer role)
- **Content-Type**: `application/x-www-form-urlencoded`

**Request Body**:
```
title=Software Developer
description=<job_description>
company_name=Tech Corp
location=New York, NY
salary_range=$50,000 - $70,000
job_type=full-time
# ... other job fields
```

**Response**: Redirect to dashboard with success/error message

## Dashboard Endpoints

### 7. Job Seeker Dashboard
- **Endpoint**: `GET /seeker_dashboard`
- **Method**: GET
- **Authentication**: Required (seeker role)

**Response**: HTML page with seeker's applications and profile info

### 8. Employer Dashboard
- **Endpoint**: `GET /employer_dashboard`
- **Method**: GET
- **Authentication**: Required (employer role)

**Response**: HTML page with posted jobs and applications

### 9. Admin Dashboard
- **Endpoint**: `GET /admin_dashboard`
- **Method**: GET
- **Authentication**: Required (admin role)

**Response**: HTML page with system statistics and management tools

## Profile Management Endpoints

### 10. View Profile
- **Endpoint**: `GET /profile`
- **Method**: GET
- **Authentication**: Required

**Response**: HTML page with user profile information

### 11. Edit Profile
- **Endpoint**: `POST /profile/edit`
- **Method**: POST
- **Authentication**: Required
- **Content-Type**: `application/x-www-form-urlencoded`

**Request Body**:
```
username=john_doe
email=john@example.com
full_name=John Doe
phone=+1234567890
location=New York, NY
bio=<user_bio>
```

**Response**: Redirect to profile page with success/error message

## Job Management Endpoints

### 12. Edit Job
- **Endpoint**: `POST /edit_job/<int:job_id>`
- **Method**: POST
- **Authentication**: Required (employer role, job owner)
- **Content-Type**: `application/x-www-form-urlencoded`
- **Path Parameters**:
  - `job_id` (integer): Job posting identifier

**Request Body**: Similar to job posting fields

**Response**: Redirect to dashboard with success/error message

### 13. Delete Job
- **Endpoint**: `POST /delete_job/<int:job_id>`
- **Method**: POST
- **Authentication**: Required (employer role, job owner)
- **Path Parameters**:
  - `job_id` (integer): Job posting identifier

**Response**: Redirect to dashboard with success/error message

### 14. Publish Job
- **Endpoint**: `POST /publish_job/<int:job_id>`
- **Method**: POST
- **Authentication**: Required (employer role, job owner)
- **Path Parameters**:
  - `job_id` (integer): Job posting identifier

**Response**: Redirect to dashboard with success/error message

## Application Management Endpoints

### 15. View Job Applications
- **Endpoint**: `GET /manage_applications/<int:job_id>`
- **Method**: GET
- **Authentication**: Required (employer role, job owner)
- **Path Parameters**:
  - `job_id` (integer): Job posting identifier

**Response**: HTML page with list of applications for the job

### 16. View Application Details
- **Endpoint**: `GET /view_application/<int:application_id>`
- **Method**: GET
- **Authentication**: Required (employer or admin role)
- **Path Parameters**:
  - `application_id` (integer): Application identifier

**Response**: HTML page with detailed application information

### 17. Update Application Status
- **Endpoint**: `POST /update_application_status/<int:application_id>`
- **Method**: POST
- **Authentication**: Required (employer or admin role)
- **Content-Type**: `application/x-www-form-urlencoded`
- **Path Parameters**:
  - `application_id` (integer): Application identifier

**Request Body**:
```
status=accepted
# status can be: pending, reviewed, accepted, rejected, withdrawn
```

**Response**: Redirect to application list with success/error message

## Administrative Endpoints

### 18. Create Admin User
- **Endpoint**: `POST /admin/create_admin`
- **Method**: POST
- **Authentication**: Required (admin role)
- **Content-Type**: `application/x-www-form-urlencoded`

**Request Body**:
```
username=admin_user
email=admin@example.com
password=secure_password
full_name=Admin User
```

**Response**: Redirect to admin dashboard with success/error message

### 19. Manage Users
- **Endpoint**: `GET /admin/manage_users`
- **Method**: GET
- **Authentication**: Required (admin role)

**Response**: HTML page with user management interface

### 20. View User Details
- **Endpoint**: `GET /admin/view_user/<int:user_id>`
- **Method**: GET
- **Authentication**: Required (admin role)
- **Path Parameters**:
  - `user_id` (integer): User identifier

**Response**: HTML page with detailed user information

### 21. Edit User
- **Endpoint**: `POST /admin/edit_user/<int:user_id>`
- **Method**: POST
- **Authentication**: Required (admin role)
- **Content-Type**: `application/x-www-form-urlencoded`
- **Path Parameters**:
  - `user_id` (integer): User identifier

**Request Body**: User profile fields

**Response**: Redirect to user management with success/error message

### 22. Deactivate User
- **Endpoint**: `POST /admin/deactivate_user/<int:user_id>`
- **Method**: POST
- **Authentication**: Required (admin role)
- **Path Parameters**:
  - `user_id` (integer): User identifier

**Response**: Redirect to user management with success/error message

### 23. Manage Jobs
- **Endpoint**: `GET /admin/manage_jobs`
- **Method**: GET
- **Authentication**: Required (admin role)

**Response**: HTML page with job management interface

### 24. Admin Reports
- **Endpoint**: `GET /admin/reports`
- **Method**: GET
- **Authentication**: Required (admin role)

**Response**: HTML page with system reports and analytics

### 25. Toggle Job Status
- **Endpoint**: `POST /admin/toggle_job_status/<int:job_id>`
- **Method**: POST
- **Authentication**: Required (admin role)
- **Path Parameters**:
  - `job_id` (integer): Job posting identifier

**Response**: Redirect to job management with success/error message

## Password Recovery Endpoints

### 26. Forgot Password
- **Endpoint**: `POST /forgot_password`
- **Method**: POST
- **Authentication**: None required
- **Content-Type**: `application/x-www-form-urlencoded`

**Request Body**:
```
email=user@example.com
```

**Response**: Redirect to login page with reset instructions

### 27. Reset Password
- **Endpoint**: `POST /reset_password/<token>`
- **Method**: POST
- **Authentication**: None required (valid token required)
- **Content-Type**: `application/x-www-form-urlencoded`
- **Path Parameters**:
  - `token` (string): Password reset token

**Request Body**:
```
password=new_secure_password
confirm_password=new_secure_password
```

**Response**: Redirect to login page with success/error message

## Utility Endpoints

### 28. Search Jobs
- **Endpoint**: `GET /search`
- **Method**: GET
- **Authentication**: Optional
- **Query Parameters**:
  - `q` (string): Search query
  - `location` (string): Location filter
  - `job_type` (string): Job type filter

**Response**: HTML page with search results

### 29. About Page
- **Endpoint**: `GET /about`
- **Method**: GET
- **Authentication**: Optional

**Response**: HTML page with application information

## Response Codes

### Success Responses
- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **302 Found**: Redirect response

### Client Error Responses
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors

### Server Error Responses
- **500 Internal Server Error**: Server-side error
- **503 Service Unavailable**: Service temporarily unavailable

## Rate Limiting

Currently, no explicit rate limiting is implemented. However, the application includes:
- Session-based request throttling
- Database connection pooling
- Request timeout handling

## Future API Enhancements

### Planned REST API
- **Versioned API endpoints** (`/api/v1/`)
- **JSON response format**
- **JWT token authentication**
- **Comprehensive error responses**
- **API documentation with Swagger/OpenAPI**

### Webhook Support
- **Real-time notifications** for job applications
- **Status update webhooks**
- **Integration endpoints** for third-party services

### Mobile API
- **Optimized endpoints** for mobile applications
- **Reduced payload sizes**
- **Offline synchronization support**

## Error Handling

### Validation Errors
Form validation errors are displayed to users with specific field-level messages.

### System Errors
- **500 errors** display a custom error page
- **Database errors** are logged and handled gracefully
- **File upload errors** provide user-friendly messages

### Logging
- **Error logging** with stack traces
- **User action logging** for audit trails
- **Performance logging** for monitoring

## Security Considerations

### Authentication
- **Session hijacking protection**
- **Secure cookie settings**
- **Password complexity requirements**

### Authorization
- **Role-based access control**
- **Route-level protection**
- **Object-level permissions**

### Data Protection
- **Input sanitization**
- **SQL injection prevention**
- **XSS protection**
- **CSRF protection**

## Testing the API

### Manual Testing
Use a web browser or tools like Postman to test the endpoints.

### Automated Testing
- **Unit tests** for route functions
- **Integration tests** for complete workflows
- **UI tests** for user interactions

### Load Testing
- **Performance testing** with Apache Bench
- **Concurrent user simulation**
- **Database load testing**

This API documentation provides a comprehensive overview of FindJob's endpoint structure and functionality. As the application evolves, this documentation should be updated to reflect new features and changes.</content>