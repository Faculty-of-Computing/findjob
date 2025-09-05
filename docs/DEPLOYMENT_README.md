# FindJob - Production Deployment Guide

## 🚀 Deploying to Render with SQLite

### Prerequisites
- GitHub repository with your FindJob project
- Render account (free tier available)

### Deployment Steps

1. **Push Code to GitHub**
   ```bash
   git add .
   git commit -m "Production deployment setup"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect and use `render.yaml`

3. **Monitor Deployment**
   - Check build logs for any errors
   - The app will be available at the provided URL once deployed

### Production Features Included

✅ **SQLite Database**: Persistent storage with 1GB disk
✅ **File Uploads**: Configured upload directory with 16MB limit
✅ **Session Management**: Filesystem-based sessions
✅ **Health Checks**: `/health` endpoint for monitoring
✅ **Gunicorn**: Production WSGI server with 2 workers
✅ **Auto-deployment**: Deploys on every GitHub push
✅ **Database Initialization**: Automatic table creation and admin user setup

### Environment Variables (Auto-configured)

- `FLASK_ENV=production`
- `FLASK_DEBUG=false`
- `SECRET_KEY` (auto-generated)
- `DATABASE_URL=sqlite:///findjob.db`
- `UPLOAD_FOLDER=/opt/render/project/src/static/uploads`
- `SESSION_FILE_DIR=/tmp/flask_sessions`
- `MAX_CONTENT_LENGTH=16777216`

### Default Admin Credentials

After deployment, you can log in with:
- **Email**: admin@findjob.com
- **Password**: admin123

⚠️ **Important**: Change the default admin password after first login!

### Troubleshooting

- **Build Failures**: Check Render logs for dependency issues
- **Database Errors**: The `init_production.py` script handles database setup
- **File Upload Issues**: Upload folder is automatically created
- **Session Issues**: Filesystem sessions are configured for production

### Local Development

1. Copy `.env.example` to `.env`
2. Install dependencies: `pip install -r requirements.txt`
3. Run locally: `python app.py`

The production setup is optimized for Render's environment and includes all necessary configurations for a robust deployment.
