# Deployment Guide for SoGoodDigital

This guide covers how to deploy your Flask application to various cloud platforms.

## Required Files for Deployment

✅ **requirements.txt** - Contains all Python dependencies including Flask and gunicorn
✅ **Procfile** - Tells the platform how to run your app
✅ **render.yaml** - Render-specific configuration
✅ **runtime.txt** - Specifies Python version
✅ **app.py** - Your main Flask application

## Environment Variables for Production

Set these environment variables in your deployment platform:

### Required
```bash
BRIGHT_DATA_API_KEY=your_bright_data_api_key_here
```

### Optional (for full functionality)
```bash
OPENAI_API_KEY=your_openai_api_key_here
TRELLO_API_KEY=your_trello_api_key_here
TRELLO_TOKEN=your_trello_token_here
TRELLO_BOARD_ID=your_trello_board_id_here
FLASK_ENV=production
PORT=5000
```

## Platform-Specific Deployment

### 1. Render.com

1. **Create a new Web Service** on [Render](https://render.com)
2. **Connect your GitHub repository**
3. **Use these settings:**
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
4. **Add environment variables** from the list above
5. **Deploy!**

### 2. Heroku

1. **Install Heroku CLI**
2. **Login and create app:**
   ```bash
   heroku login
   heroku create your-app-name
   ```
3. **Set environment variables:**
   ```bash
   heroku config:set BRIGHT_DATA_API_KEY=your_api_key_here
   heroku config:set FLASK_ENV=production
   ```
4. **Deploy:**
   ```bash
   git push heroku main
   ```

### 3. Railway

1. **Connect GitHub repository** on [Railway](https://railway.app)
2. **Add environment variables** in the dashboard
3. **Deploy automatically** from GitHub

### 4. Google Cloud Platform

1. **Create App Engine app:**
   ```bash
   gcloud app create
   ```
2. **Create app.yaml:**
   ```yaml
   runtime: python311
   env_variables:
     BRIGHT_DATA_API_KEY: "your_api_key_here"
     FLASK_ENV: "production"
   ```
3. **Deploy:**
   ```bash
   gcloud app deploy
   ```

## Local Testing Before Deployment

Test your app locally with production settings:

```bash
# Set environment variables
export FLASK_ENV=production
export PORT=5000
export BRIGHT_DATA_API_KEY=your_api_key_here

# Test with gunicorn (same as production)
gunicorn app:app --bind 0.0.0.0:5000 --workers 1 --timeout 120

# Or test with Flask development server
python app.py
```

## Common Deployment Issues and Solutions

### 1. "gunicorn: command not found"
**Solution:** Make sure `gunicorn>=21.2.0` is in requirements.txt

### 2. "No module named 'Flask'"
**Solution:** Make sure `Flask>=2.3.0` is in requirements.txt

### 3. "Application timeout"
**Solution:** Increase timeout in gunicorn command: `--timeout 120`

### 4. "Memory issues"
**Solution:** Reduce workers: `--workers 1` or upgrade plan

### 5. "Environment variables not found"
**Solution:** Double-check environment variable names and values in your platform

### 6. "Import errors"
**Solution:** Check that all dependencies are in requirements.txt with correct versions

## Performance Optimization

### For Production:
1. **Set workers based on CPU cores:** `--workers 2` (for more CPU)
2. **Enable keep-alive:** `--keep-alive 2`
3. **Set appropriate timeout:** `--timeout 120`
4. **Use appropriate worker class:** `--worker-class sync`

### Example optimized start command:
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100
```

## Monitoring and Logs

### Check logs on different platforms:

**Render:**
```bash
# View logs in Render dashboard or CLI
render logs --service your-service-name
```

**Heroku:**
```bash
heroku logs --tail --app your-app-name
```

**Railway:**
```bash
# View logs in Railway dashboard
```

## Security Considerations

1. **Never commit API keys** to your repository
2. **Use environment variables** for all secrets
3. **Set FLASK_ENV=production** in production
4. **Use HTTPS** (most platforms provide this automatically)
5. **Regularly update dependencies**

## Cost Optimization

1. **Use free tiers** for testing: Render, Heroku, Railway all offer free tiers
2. **Scale workers** based on actual traffic
3. **Monitor usage** and adjust resources accordingly
4. **Use appropriate instance sizes**

## Quick Deploy Checklist

Before deploying, ensure:

- [ ] All API keys are set as environment variables
- [ ] requirements.txt includes Flask and gunicorn
- [ ] Procfile exists with correct command
- [ ] runtime.txt specifies Python version
- [ ] No secrets in git repository
- [ ] App works locally with gunicorn
- [ ] Environment variables are configured in platform
- [ ] FLASK_ENV=production is set

## Support

If you encounter issues:

1. **Check platform-specific documentation**
2. **Review application logs** for error details
3. **Test locally** with the same configuration
4. **Verify environment variables** are set correctly
5. **Check requirements.txt** for missing dependencies 