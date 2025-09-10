@echo off
echo Installing cryptography for SSL...
pip install cryptography
echo Generating SSL certificate...
python generate_cert.py
echo SSL setup complete!
echo Run: python run_app_clean.py
pause