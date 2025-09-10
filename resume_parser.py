import PyPDF2
import docx
import re
from typing import Dict, List

class ResumeParser:
    def __init__(self):
        self.skills_keywords = [
            'python', 'java', 'javascript', 'react', 'node.js', 'aws', 'docker', 
            'kubernetes', 'sql', 'mongodb', 'git', 'agile', 'scrum', 'ci/cd'
        ]
    
    def extract_text(self, file_path: str) -> str:
        if file_path.endswith('.pdf'):
            return self._extract_pdf(file_path)
        elif file_path.endswith('.docx'):
            return self._extract_docx(file_path)
        raise ValueError("Unsupported file format")
    
    def _extract_pdf(self, file_path: str) -> str:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return ''.join(page.extract_text() for page in reader.pages)
    
    def _extract_docx(self, file_path: str) -> str:
        doc = docx.Document(file_path)
        return '\n'.join(paragraph.text for paragraph in doc.paragraphs)
    
    def parse_resume(self, file_path: str) -> Dict:
        text = self.extract_text(file_path).lower()
        
        # Extract skills
        skills = [skill for skill in self.skills_keywords if skill in text]
        
        # Extract experience (years)
        exp_match = re.search(r'(\d+)\s*(?:years?|yrs?)', text)
        experience = int(exp_match.group(1)) if exp_match else 0
        
        # Calculate ATS score
        ats_score = min(100, len(skills) * 10 + experience * 5)
        
        # Calculate technical depth based on skills and experience
        technical_depth = min(100, len(skills) * 8 + experience * 3)
        leadership_score = min(100, experience * 10)
        
        return {
            'skills': skills,
            'experience_years': experience,
            'ats_score': ats_score,
            'technical_depth': technical_depth,
            'leadership_score': leadership_score,
            'raw_text': text[:500]  # First 500 chars for context
        }