#!/usr/bin/env python3
"""
Test AWS Q Question Generation
"""

import subprocess
import sys
import os
import json

def test_amazon_q_cli():
    """Test if Amazon Q CLI is working for question generation"""
    
    # Check if we have a resume file to test with
    resume_files = []
    uploads_dir = "uploads"
    
    if os.path.exists(uploads_dir):
        for file in os.listdir(uploads_dir):
            if file.lower().endswith(('.pdf', '.docx')):
                resume_files.append(os.path.join(uploads_dir, file))
    
    if not resume_files:
        print("❌ No resume files found in uploads/ directory")
        print("Please upload a resume first through the web interface")
        return False
    
    resume_file = resume_files[0]
    print(f"📄 Testing with resume: {resume_file}")
    
    try:
        # Test Amazon Q CLI for questions
        print("\n🔍 Testing Amazon Q CLI question generation...")
        
        cmd = [sys.executable, 'amazon_q_simple.py', 'questions', '--resume', resume_file, '--role', 'Software Engineer']
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        
        if result.returncode == 0:
            # Check if output contains questions
            output = result.stdout
            
            if "GENERATED QUESTIONS" in output:
                print("✅ Amazon Q CLI is working - questions generated!")
                
                # Try to extract JSON from output
                if '{' in output and '}' in output:
                    try:
                        start = output.find('{')
                        end = output.rfind('}') + 1
                        json_str = output[start:end]
                        questions_data = json.loads(json_str)
                        
                        if 'questions' in questions_data:
                            questions = questions_data['questions']
                            print(f"📝 Found {len(questions)} questions:")
                            for i, q in enumerate(questions, 1):
                                print(f"   {i}. {q}")
                            return True
                    except json.JSONDecodeError:
                        pass
                
                print("✅ Questions generated but not in JSON format")
                return True
            else:
                print("⚠️ Amazon Q CLI ran but no questions found in output")
                return False
        else:
            print("❌ Amazon Q CLI failed")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Amazon Q CLI timeout")
        return False
    except Exception as e:
        print(f"❌ Error testing Amazon Q CLI: {e}")
        return False

def test_flask_integration():
    """Test Flask integration with Amazon Q"""
    
    print("\n🌐 Testing Flask integration...")
    
    try:
        import requests
        
        # Test if Flask app is running
        response = requests.get('http://localhost:5003', timeout=5)
        
        if response.status_code == 200:
            print("✅ Flask app is running")
            
            # You can add more tests here for the Flask endpoints
            # For example, testing the /get_current_question endpoint
            
            return True
        else:
            print(f"⚠️ Flask app returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Flask app is not running")
        print("Start it with: python amazon_q_voice_app.py")
        return False
    except ImportError:
        print("⚠️ requests library not installed")
        print("Install with: pip install requests")
        return False
    except Exception as e:
        print(f"❌ Error testing Flask: {e}")
        return False

def main():
    print("🧪 AWS Q Question Generation Test")
    print("=" * 50)
    
    # Test 1: Amazon Q CLI
    cli_works = test_amazon_q_cli()
    
    # Test 2: Flask integration
    flask_works = test_flask_integration()
    
    print("\n📊 Test Results:")
    print("=" * 50)
    print(f"Amazon Q CLI: {'✅ Working' if cli_works else '❌ Failed'}")
    print(f"Flask Integration: {'✅ Working' if flask_works else '❌ Failed'}")
    
    if cli_works and flask_works:
        print("\n🎉 All tests passed! AWS Q is generating questions.")
    elif cli_works:
        print("\n⚠️ Amazon Q CLI works, but Flask app needs to be started.")
        print("Run: python amazon_q_voice_app.py")
    else:
        print("\n❌ Issues found. Check the error messages above.")
    
    print("\n💡 To verify questions in the web interface:")
    print("1. Start the app: python amazon_q_voice_app.py")
    print("2. Upload a resume")
    print("3. Start voice interview")
    print("4. Check if questions appear (not 'undefined')")

if __name__ == "__main__":
    main()