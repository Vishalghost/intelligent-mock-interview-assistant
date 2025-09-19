#!/usr/bin/env python3
"""
Simple test for AWS Q question generation
"""

import subprocess
import sys
import os
import json

def test_questions():
    print("AWS Q Question Generation Test")
    print("=" * 40)
    
    # Find a resume file
    resume_files = []
    if os.path.exists("uploads"):
        for file in os.listdir("uploads"):
            if file.lower().endswith(('.pdf', '.docx')):
                resume_files.append(os.path.join("uploads", file))
    
    if not resume_files:
        print("No resume files found in uploads/")
        print("Upload a resume first through the web interface")
        return
    
    resume_file = resume_files[0]
    print(f"Testing with: {resume_file}")
    
    try:
        # Test the Amazon Q CLI
        cmd = [sys.executable, 'amazon_q_simple.py', 'questions', '--resume', resume_file, '--role', 'Software Engineer']
        
        print("\nRunning Amazon Q CLI...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print(f"Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("SUCCESS: Amazon Q CLI worked!")
            print("\nOutput:")
            print(result.stdout)
            
            # Check for questions in output
            if "1." in result.stdout and "2." in result.stdout:
                print("\nQUESTIONS FOUND: AWS Q is generating questions!")
            else:
                print("\nNo numbered questions found in output")
        else:
            print("FAILED: Amazon Q CLI error")
            print("Error:", result.stderr)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_questions()