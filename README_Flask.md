# Google Scholar Research Agent - Web Interface

A beautiful web interface for the Google Scholar Research Agent that provides AI-powered research synthesis from Google Scholar papers.

## 🌟 Features

- **Modern Web Interface**: Beautiful, responsive design with Bootstrap 5
- **Real-time Progress**: Live updates using Socket.IO during analysis
- **Google Integration**: Seamless integration with Google Docs, Sheets, and Slides
- **AI-Powered Analysis**: Advanced keyword extraction and research synthesis
- **Multiple Output Formats**: Generate both Google Docs and Word documents
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Mobile Responsive**: Works perfectly on desktop, tablet, and mobile devices

## 📋 Prerequisites

Before running the web interface, make sure you have:

1. **Python 3.8+** installed
2. **Google Scholar Research Agent** (the main `google_scholar_research_agent.py` file)
3. **Google Service Account** credentials set up
4. **OpenAI API Key** configured

## 🚀 Quick Start

### 1. Install Flask Dependencies

```bash
pip install -r flask_requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in your project directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_SERVICE_ACCOUNT_PATH=path/to/your/service-account.json
TWOCAPTCHA_API_KEY=your_2captcha_api_key_here  # Optional
```

### 3. Run the Application

```bash
python run_flask.py
```

Or run directly:

```bash
python app.py
```

### 4. Open Your Browser

Navigate to: `http://localhost:8080`

## 📁 Project Structure

```
├── app.py                      # Main Flask application
├── run_flask.py               # Simple run script
├── flask_requirements.txt     # Flask-specific dependencies
├── google_scholar_research_agent.py  # Core research agent
├── templates/                 # HTML templates
│   ├── base.html             # Base template
│   ├── index.html            # Dashboard
│   ├── analyze.html          # Analysis form
│   ├── progress.html         # Progress tracking
│   ├── results.html          # Results display
│   └── error.html            # Error pages
├── static/                    # Static assets
│   ├── css/
│   │   └── style.css         # Custom styles
│   └── js/
│       └── app.js            # Custom JavaScript
└── README_Flask.md           # This file
```

## 🎯 How to Use

### Step 1: Prepare Your Google File

1. Create a Google Doc, Sheet, or Slide with your research topic
2. Note the File ID from the URL (the long string after `/d/`)
3. Share the file with your service account email:
   - `sebastiancastano@phonic-goods-317118.iam.gserviceaccount.com`
   - Set permission to "Viewer" or "Editor"

### Step 2: Start Analysis

1. Go to the **Analyze** page
2. Enter your Google File ID
3. Choose your output format
4. Click **Start Analysis**

### Step 3: Monitor Progress

- View real-time progress updates
- See detailed logs of the analysis process
- Get notifications for each completed step

### Step 4: View Results

- Access generated Google Docs and Word documents
- Review comprehensive research synthesis
- Download files for offline use

## 🔧 Configuration Options

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `GOOGLE_SERVICE_ACCOUNT_PATH` | Yes | Path to Google service account JSON |
| `TWOCAPTCHA_API_KEY` | No | 2captcha API key for CAPTCHA solving |
| `FLASK_ENV` | No | Flask environment (development/production) |
| `FLASK_DEBUG` | No | Enable Flask debug mode |

### Application Settings

You can modify these settings in `app.py`:

- `MAX_CONTENT_LENGTH`: Maximum file upload size
- `PERMANENT_SESSION_LIFETIME`: Session timeout
- Socket.IO settings for real-time updates

## 🌐 API Endpoints

### Web Routes

- `GET /` - Dashboard
- `GET /analyze` - Analysis form
- `POST /analyze` - Start analysis
- `GET /progress/<task_id>` - Progress tracking
- `GET /results/<task_id>` - View results
- `GET /download/<filename>` - Download files

### API Routes

- `GET /api/status/<task_id>` - Get analysis status
- `POST /api/cancel/<task_id>` - Cancel analysis

### Socket.IO Events

- `join_task` - Join task room for updates
- `status_update` - Receive progress updates
- `connect` / `disconnect` - Connection events

## 🎨 Customization

### Styling

Modify `static/css/style.css` to customize:
- Colors and themes
- Layout and spacing
- Animations and effects
- Responsive breakpoints

### Templates

Edit HTML templates in `templates/` to:
- Change page layouts
- Add new sections
- Modify content structure
- Update branding

### JavaScript

Enhance `static/js/app.js` to:
- Add new interactive features
- Customize form validation
- Implement additional animations
- Extend utility functions

## 🔍 Troubleshooting

### Common Issues

**1. "File access denied" error**
- Make sure your Google file is shared with the service account
- Check that the File ID is correct
- Verify service account permissions

**2. Analysis fails to start**
- Check OpenAI API key configuration
- Verify internet connection
- Ensure all dependencies are installed

**3. Real-time updates not working**
- Check Socket.IO connection in browser console
- Verify firewall settings
- Try refreshing the page

**4. Slow analysis performance**
- This is normal for large document analysis
- Consider using fewer search queries
- Check network connection speed

### Debug Mode

Run in debug mode for detailed error information:

```bash
FLASK_DEBUG=1 python app.py
```

### Log Files

Check console output for detailed logs during analysis.

## 📱 Mobile Support

The web interface is fully responsive and works on:
- Desktop computers (Chrome, Firefox, Safari, Edge)
- Tablets (iPad, Android tablets)
- Mobile phones (iPhone, Android phones)

## 🔒 Security Notes

- Keep your OpenAI API key secure
- Don't commit credentials to version control
- Use HTTPS in production environments
- Regularly update dependencies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:

1. Check this README for common solutions
2. Review the console logs for error details
3. Ensure all prerequisites are met
4. Try restarting the application

## 🚀 Deployment

### Local Development
```bash
python run_flask.py
```

### Production Deployment
For production deployment, consider:
- Using a production WSGI server (Gunicorn, uWSGI)
- Setting up reverse proxy (Nginx)
- Configuring SSL certificates
- Using environment-specific configuration

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:8080 app:app
```

---

**Enjoy using the Google Scholar Research Agent Web Interface! 🎉** 