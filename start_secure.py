import os
import subprocess
from professional_app import app

# Set API key if not already set
if not os.getenv('DEEPSEEK_API_KEY'):
    os.environ['DEEPSEEK_API_KEY'] = 'demo-key-disabled'

# Generate SSL cert if not exists
if not os.path.exists('cert.pem'):
    try:
        subprocess.run(['python', 'generate_cert.py'], check=True)
        print("SSL certificates generated")
    except:
        print("SSL generation failed, using HTTP")

if __name__ == '__main__':
    print("Starting Interview Assistant")
    if os.path.exists('cert.pem'):
        print("HTTPS: https://localhost:5002")
        app.run(host='0.0.0.0', port=5002, ssl_context=('cert.pem', 'key.pem'))
    else:
        print("HTTP: http://localhost:5002")
        app.run(host='0.0.0.0', port=5002)