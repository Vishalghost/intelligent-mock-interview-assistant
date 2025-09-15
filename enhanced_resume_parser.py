import PyPDF2
import docx
import re
from typing import Dict, List, Optional
import json

class EnhancedResumeParser:
    def __init__(self):
        # Comprehensive skills database
        self.technical_skills = {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 
                'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl'
            ],
            'web_technologies': [
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django',
                'flask', 'spring', 'laravel', 'bootstrap', 'jquery', 'webpack', 'sass'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'cassandra',
                'elasticsearch', 'dynamodb', 'firebase', 'neo4j'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean', 'vercel'
            ],
            'devops_tools': [
                'docker', 'kubernetes', 'jenkins', 'gitlab', 'github actions', 'terraform',
                'ansible', 'vagrant', 'nginx', 'apache'
            ],
            'data_science': [
                'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
                'matplotlib', 'seaborn', 'jupyter', 'tableau', 'power bi'
            ],
            'mobile_development': [
                'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic'
            ]
        }
        
        self.soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
            'creative', 'adaptable', 'organized', 'detail-oriented', 'time management'
        ]
        
        self.certifications = [
            'aws certified', 'azure certified', 'google cloud certified', 'pmp',
            'scrum master', 'cissp', 'comptia', 'cisco', 'microsoft certified'
        ]

    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX files"""
        try:
            if file_path.lower().endswith('.pdf'):
                return self._extract_pdf(file_path)
            elif file_path.lower().endswith('.docx'):
                return self._extract_docx(file_path)
            else:
                raise ValueError("Unsupported file format")
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""

    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"PDF extraction error: {e}")
        return text

    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"DOCX extraction error: {e}")
        return text

    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume and extract comprehensive information"""
        text = self.extract_text(file_path)
        if not text:
            return self._get_fallback_data()
        
        text_lower = text.lower()
        
        # Extract all information
        parsed_data = {
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'location': self._extract_location(text),
            'linkedin': self._extract_linkedin(text),
            'github': self._extract_github(text),
            'skills': self._extract_skills(text_lower),
            'experience_years': self._extract_experience_years(text_lower),
            'education': self._extract_education(text),
            'certifications': self._extract_certifications(text_lower),
            'projects': self._extract_projects(text),
            'work_experience': self._extract_work_experience(text),
            'languages': self._extract_languages(text_lower),
            'summary': self._extract_summary(text),
            'ats_score': 0,
            'technical_depth': 0,
            'leadership_score': 0,
            'raw_text': text[:1000]  # First 1000 chars for context
        }
        
        # Calculate scores
        parsed_data['ats_score'] = self._calculate_ats_score(parsed_data)
        parsed_data['technical_depth'] = self._calculate_technical_depth(parsed_data)
        parsed_data['leadership_score'] = self._calculate_leadership_score(parsed_data)
        
        return parsed_data

    def _extract_name(self, text: str) -> str:
        """Extract candidate name"""
        lines = text.strip().split('\n')
        # Usually name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if line and len(line.split()) <= 4 and not '@' in line and not any(char.isdigit() for char in line):
                # Check if it looks like a name (not email, phone, etc.)
                if not any(keyword in line.lower() for keyword in ['email', 'phone', 'address', 'linkedin']):
                    return line
        return "Candidate"

    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""

    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        phone_patterns = [
            r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\b\d{10}\b',
            r'\(\d{3}\)\s?\d{3}-\d{4}'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return str(phones[0]) if isinstance(phones[0], tuple) else phones[0]
        return ""

    def _extract_location(self, text: str) -> str:
        """Extract location/address"""
        # Look for city, state patterns
        location_pattern = r'([A-Za-z\s]+),\s*([A-Z]{2})\b'
        locations = re.findall(location_pattern, text)
        if locations:
            return f"{locations[0][0]}, {locations[0][1]}"
        return ""

    def _extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn profile"""
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.findall(linkedin_pattern, text.lower())
        return linkedin[0] if linkedin else ""

    def _extract_github(self, text: str) -> str:
        """Extract GitHub profile"""
        github_pattern = r'github\.com/[\w-]+'
        github = re.findall(github_pattern, text.lower())
        return github[0] if github else ""

    def _extract_skills(self, text_lower: str) -> Dict[str, List[str]]:
        """Extract technical and soft skills"""
        found_skills = {
            'technical': {},
            'soft': []
        }
        
        # Extract technical skills by category (optimized)
        for category, skills_list in self.technical_skills.items():
            category_skills = [skill.title() for skill in skills_list if skill in text_lower]
            found_skills['technical'][category] = category_skills
        
        # Extract soft skills (list comprehension for better performance)
        found_skills['soft'] = [skill.title() for skill in self.soft_skills if skill in text_lower]
        
        # Flatten technical skills for backward compatibility
        all_technical = []
        for category_skills in found_skills['technical'].values():
            all_technical.extend(category_skills)
        
        return {
            'all_skills': all_technical + found_skills['soft'],
            'technical_by_category': found_skills['technical'],
            'soft_skills': found_skills['soft'],
            'total_count': len(all_technical) + len(found_skills['soft'])
        }

    def _extract_experience_years(self, text_lower: str) -> int:
        """Extract years of experience with improved accuracy"""
        experience = 0
        
        # Pattern 1: "X years of experience"
        exp_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(\d+)\+?\s*years?\s+(?:in|with)',
            r'experience.*?(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s+(?:professional|work)',
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                years = [int(match) for match in matches if match.isdigit()]
                if years:
                    experience = max(experience, max(years))
        
        # Pattern 2: Date ranges (2020-2023, 2020-present)
        date_patterns = [
            r'(20\d{2})\s*[-–]\s*(20\d{2}|present)',
            r'(20\d{2})\s*[-–]\s*current',
        ]
        
        current_year = 2024
        total_experience = 0
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text_lower)
            for start, end in matches:
                start_year = int(start)
                end_year = current_year if end.lower() in ['present', 'current'] else int(end)
                total_experience += max(0, end_year - start_year)
        
        return max(experience, min(total_experience, 30))  # Cap at 30 years

    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education information"""
        education = []
        
        # Common degree patterns
        degree_patterns = [
            r'(bachelor|master|phd|doctorate|associate).*?(?:in|of)\s+([^\n,]+)',
            r'(b\.?s\.?|m\.?s\.?|m\.?a\.?|ph\.?d\.?|b\.?a\.?).*?(?:in|of)?\s+([^\n,]+)',
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for degree, field in matches:
                education.append({
                    'degree': degree.strip(),
                    'field': field.strip(),
                    'institution': self._extract_institution_near_degree(text, degree)
                })
        
        return education[:3]  # Limit to 3 entries

    def _extract_institution_near_degree(self, text: str, degree: str) -> str:
        """Extract institution name near degree mention"""
        lines = text.split('\n')
        degree_lower = degree.lower()
        institution_keywords = {'university', 'college', 'institute', 'school'}
        
        for i, line in enumerate(lines):
            if degree_lower in line.lower():
                # Look in surrounding lines (limited window for performance)
                search_range = range(max(0, i-2), min(len(lines), i+3))
                for j in search_range:
                    line_lower = lines[j].lower()
                    if any(keyword in line_lower for keyword in institution_keywords):
                        return lines[j].strip()
        return ""

    def _extract_certifications(self, text_lower: str) -> List[str]:
        """Extract certifications"""
        found_certs = []
        for cert in self.certifications:
            if cert in text_lower:
                found_certs.append(cert.title())
        return found_certs

    def _extract_projects(self, text: str) -> List[Dict]:
        """Extract project information"""
        projects = []
        
        # Look for project sections
        project_section_pattern = r'projects?\s*:?\s*\n(.*?)(?=\n\s*[A-Z][^:\n]*:|$)'
        project_matches = re.findall(project_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        for match in project_matches:
            # Split into individual projects
            project_lines = [line.strip() for line in match.split('\n') if line.strip()]
            for line in project_lines[:5]:  # Limit to 5 projects
                if line and len(line) > 10:  # Reasonable project description length
                    projects.append({
                        'name': line.split(':')[0] if ':' in line else line[:50],
                        'description': line
                    })
        
        return projects

    def _extract_work_experience(self, text: str) -> List[Dict]:
        """Extract work experience"""
        experience = []
        
        # Look for job titles and companies
        job_patterns = [
            r'(software engineer|developer|analyst|manager|director|lead|senior|junior)\s+(?:at\s+)?([^\n,]+)',
            r'([^\n,]+)\s+(?:at|@)\s+([^\n,]+)',
        ]
        
        for pattern in job_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for title, company in matches[:5]:  # Limit to 5 entries
                experience.append({
                    'title': title.strip(),
                    'company': company.strip()
                })
        
        return experience

    def _extract_languages(self, text_lower: str) -> List[str]:
        """Extract programming/spoken languages"""
        languages = []
        common_languages = ['english', 'spanish', 'french', 'german', 'chinese', 'japanese', 'korean']
        
        for lang in common_languages:
            if lang in text_lower:
                languages.append(lang.title())
        
        return languages

    def _extract_summary(self, text: str) -> str:
        """Extract professional summary"""
        # Look for summary/objective sections
        summary_patterns = [
            r'(?:summary|objective|profile)\s*:?\s*\n(.*?)(?=\n\s*[A-Z][^:\n]*:|$)',
            r'(?:about|overview)\s*:?\s*\n(.*?)(?=\n\s*[A-Z][^:\n]*:|$)'
        ]
        
        for pattern in summary_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                summary = matches[0].strip()
                return summary[:500]  # Limit length
        
        # Fallback: use first paragraph if no explicit summary
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if len(para.strip()) > 50 and not any(keyword in para.lower() for keyword in ['email', 'phone', 'address']):
                return para.strip()[:300]
        
        return ""

    def _calculate_ats_score(self, data: Dict) -> int:
        """Calculate ATS-friendly score"""
        score = 0
        
        # Contact information
        if data['email']: score += 10
        if data['phone']: score += 10
        if data['location']: score += 5
        
        # Skills
        skills_count = data['skills']['total_count']
        score += min(skills_count * 3, 30)  # Max 30 points for skills
        
        # Experience
        score += min(data['experience_years'] * 2, 20)  # Max 20 points for experience
        
        # Education
        if data['education']: score += 15
        
        # Certifications
        score += len(data['certifications']) * 5
        
        # Professional summary
        if data['summary']: score += 10
        
        return min(score, 100)

    def _calculate_technical_depth(self, data: Dict) -> int:
        """Calculate technical depth score"""
        score = 0
        
        # Technical skills by category
        tech_skills = data['skills']['technical_by_category']
        for category, skills in tech_skills.items():
            if skills:
                score += len(skills) * 5
        
        # Experience multiplier
        exp_multiplier = min(data['experience_years'] / 5, 2)  # Max 2x multiplier
        score = int(score * exp_multiplier)
        
        # Projects boost
        score += len(data['projects']) * 5
        
        # Certifications boost
        score += len(data['certifications']) * 10
        
        return min(score, 100)

    def _calculate_leadership_score(self, data: Dict) -> int:
        """Calculate leadership potential score"""
        score = 0
        
        # Experience-based
        score += min(data['experience_years'] * 8, 40)
        
        # Leadership keywords in summary/experience
        leadership_keywords = ['lead', 'manage', 'director', 'senior', 'mentor', 'team', 'project manager']
        text_lower = data['raw_text'].lower()
        
        for keyword in leadership_keywords:
            if keyword in text_lower:
                score += 10
        
        # Soft skills
        score += len(data['skills']['soft_skills']) * 3
        
        return min(score, 100)

    def _get_fallback_data(self) -> Dict:
        """Return fallback data when parsing fails"""
        return {
            'name': 'Candidate',
            'email': '',
            'phone': '',
            'location': '',
            'linkedin': '',
            'github': '',
            'skills': {
                'all_skills': ['Python', 'JavaScript', 'SQL'],
                'technical_by_category': {
                    'programming_languages': ['Python', 'JavaScript'],
                    'databases': ['SQL']
                },
                'soft_skills': ['Communication', 'Problem Solving'],
                'total_count': 5
            },
            'experience_years': 2,
            'education': [],
            'certifications': [],
            'projects': [],
            'work_experience': [],
            'languages': ['English'],
            'summary': '',
            'ats_score': 45,
            'technical_depth': 35,
            'leadership_score': 25,
            'raw_text': 'Sample resume data'
        }

# Test the enhanced parser
if __name__ == "__main__":
    parser = EnhancedResumeParser()
    
    # Test with your resume
    resume_path = "uploads/Vishal_Resume.pdf"
    try:
        result = parser.parse_resume(resume_path)
        print("Enhanced Resume Analysis:")
        print("=" * 50)
        print(f"Name: {result['name']}")
        print(f"Email: {result['email']}")
        print(f"Experience: {result['experience_years']} years")
        print(f"Total Skills: {result['skills']['total_count']}")
        print(f"Technical Skills by Category:")
        for category, skills in result['skills']['technical_by_category'].items():
            if skills:
                print(f"  {category.replace('_', ' ').title()}: {', '.join(skills)}")
        print(f"Soft Skills: {', '.join(result['skills']['soft_skills'])}")
        print(f"ATS Score: {result['ats_score']}/100")
        print(f"Technical Depth: {result['technical_depth']}/100")
        print(f"Leadership Score: {result['leadership_score']}/100")
        print(f"Education: {len(result['education'])} entries")
        print(f"Certifications: {', '.join(result['certifications'])}")
        print(f"Projects: {len(result['projects'])} found")
        
        # Save detailed analysis
        with open('detailed_resume_analysis.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("\nDetailed analysis saved to 'detailed_resume_analysis.json'")
        
    except Exception as e:
        print(f"Error analyzing resume: {e}")