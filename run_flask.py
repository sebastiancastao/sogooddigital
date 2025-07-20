"""
Simple script to run the Google Scholar Research Agent Flask application
"""

import os
import sys
from app import app, socketio

if __name__ == '__main__':
    # Set environment variables for development
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    print("🚀 Starting Google Scholar Research Agent Web Interface...")
    print(f"📱 Open your browser and go to: http://localhost:8080")
    print("🔄 Use Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run the Flask-SocketIO application
        socketio.run(app, 
                    host='0.0.0.0', 
                    port=8080, 
                    debug=True,
                    use_reloader=True,
                    log_output=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1) 