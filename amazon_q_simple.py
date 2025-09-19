#!/usr/bin/env python3
"""
Simple Amazon Q CLI Integration without sensitive data
"""

import json
import os
import sys
from datetime import datetime
import argparse
import PyPDF2
from docx import Document
import re

def extract_text_from_file(file_path):
    """Extract text from PDF or DOCX file"""
    try:
        if file_path.lower().endswith('.pdf'):
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        elif file_path.lower().endswith('.docx'):
            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def analyze_resume_simple(file_path, target_role):
    """Simple resume analysis"""
    text = extract_text_from_file(file_path)
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    # Extract name (first line)
    lines = text.split('\n')
    name = lines[0].strip() if lines else "Candidate"
    
    # Extract skills
    tech_skills = ['Python', 'Java', 'JavaScript', 'React', 'Node.js', 'Angular', 'Vue',
                   'Django', 'Flask', 'Spring', 'Docker', 'Kubernetes', 'AWS', 'Azure',
                   'SQL', 'MongoDB', 'PostgreSQL', 'Git', 'Linux', 'HTML', 'CSS', 'TypeScript']
    
    found_skills = []
    text_lower = text.lower()
    for skill in tech_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    # Calculate experience years
    year_pattern = r'\b(19|20)\d{2}\b'
    years = re.findall(year_pattern, text)
    experience_years = max(0, max([int(y) for y in years]) - min([int(y) for y in years])) if len(years) >= 2 else 2
    
    result = {
        "candidate_info": {
            "name": name,
            "email": emails[0] if emails else "",
            "phone": "",
            "location": ""
        },
        "skills": found_skills,
        "professional_profile": {
            "experience_years": experience_years,
            "domain_expertise": "Software Development",
            "seniority_level": "Senior" if experience_years >= 8 else "Mid-level" if experience_years >= 3 else "Junior"
        },
        "assessment_scores": {
            "ats_score": min(100, 60 + len(found_skills) * 3),
            "technical_depth": min(100, len(found_skills) * 8),
            "leadership_potential": min(100, 30 + experience_years * 5)
        },
        "target_role": target_role
    }
    
    return result

def generate_questions_simple(role, skills):
    """Generate simple interview questions"""
    questions = [
        f"Tell me about your experience with {skills[0] if skills else 'programming'} and how you've used it in projects.",
        f"Describe a challenging {role.lower()} project you worked on and how you solved technical problems.",
        "How do you approach debugging and troubleshooting issues in your code?",
        "Explain your understanding of software development best practices.",
        "Tell me about a time when you had to learn a new technology quickly."
    ]
    
    return {
        "role": role,
        "questions": questions,
        "total_questions": len(questions),
        "estimated_duration": 25
    }

def main():
    parser = argparse.ArgumentParser(description='Simple Amazon Q CLI Integration')
    parser.add_argument('command', choices=['analyze', 'questions', 'interview'])
    parser.add_argument('--resume', '-r', required=True)
    parser.add_argument('--role', '-role', default='Software Engineer')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.resume):
        print(f"Resume file not found: {args.resume}")
        return
    
    if args.command == 'analyze':
        result = analyze_resume_simple(args.resume, args.role)
        print("RESUME ANALYSIS RESULTS")
        print("=" * 50)
        print(f"Name: {result['candidate_info']['name']}")
        print(f"Email: {result['candidate_info']['email']}")
        print(f"Experience: {result['professional_profile']['experience_years']} years")
        print(f"Skills: {', '.join(result['skills'])}")
        print(f"ATS Score: {result['assessment_scores']['ats_score']}/100")
        print(json.dumps(result, indent=2))
        
    elif args.command == 'questions':
        analysis = analyze_resume_simple(args.resume, args.role)
        questions = generate_questions_simple(args.role, analysis['skills'])
        print("GENERATED QUESTIONS")
        print("=" * 50)
        for i, q in enumerate(questions['questions'], 1):
            print(f"{i}. {q}")
        print(json.dumps(questions, indent=2))
        
    elif args.command == 'interview':
        analysis = analyze_resume_simple(args.resume, args.role)
        questions = generate_questions_simple(args.role, analysis['skills'])
        print("INTERVIEW SIMULATION COMPLETE")
        print("=" * 50)
        print(f"Candidate: {analysis['candidate_info']['name']}")
        print(f"Role: {args.role}")
        print(f"Questions: {len(questions['questions'])}")
        print("Analysis and questions generated successfully")

if __name__ == "__main__":
    main()