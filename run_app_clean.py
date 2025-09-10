import sys
import os

# Set UTF-8 encoding for stdout/stderr
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Import and run the main app
from professional_app import app

if __name__ == '__main__':
    print("Starting Professional Interview Assessment Platform")
    
    if os.path.exists('cert.pem') and os.path.exists('key.pem'):
        print("HTTPS Server starting...")
        print("Visit: https://localhost:5002")
        app.run(host='0.0.0.0', port=5002, debug=False, ssl_context=('cert.pem', 'key.pem'))
    else:
        print("HTTP Server starting...")
        print("Visit: http://localhost:5002")
        app.run(host='0.0.0.0', port=5002, debug=False)