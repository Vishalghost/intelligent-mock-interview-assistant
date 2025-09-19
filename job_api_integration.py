#!/usr/bin/env python3
"""
Real Job API Integration
Integrates with multiple job APIs to fetch real job postings
"""

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class JobAPIIntegrator:
    def __init__(self):
        # API Keys (add to .env file)
        self.adzuna_app_id = os.getenv('ADZUNA_APP_ID')
        self.adzuna_api_key = os.getenv('ADZUNA_API_KEY')
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        
    def search_adzuna_jobs(self, title, location="United States", results_per_page=10):
        """Search jobs using Adzuna API (free tier available)"""
        if not self.adzuna_app_id or not self.adzuna_api_key:
            return {"error": "Adzuna API credentials not configured"}
        
        try:
            url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
            params = {
                'app_id': self.adzuna_app_id,
                'app_key': self.adzuna_api_key,
                'what': title,
                'where': location,
                'results_per_page': results_per_page,
                'sort_by': 'relevance'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                jobs = []
                
                for job in data.get('results', []):
                    jobs.append({
                        'title': job.get('title', ''),
                        'company': job.get('company', {}).get('display_name', ''),
                        'location': job.get('location', {}).get('display_name', ''),
                        'salary_min': job.get('salary_min'),
                        'salary_max': job.get('salary_max'),
                        'description': job.get('description', '')[:500] + '...',
                        'url': job.get('redirect_url', ''),
                        'created': job.get('created', ''),
                        'source': 'Adzuna'
                    })
                
                return {
                    'jobs': jobs,
                    'total_count': data.get('count', 0),
                    'source': 'Adzuna API'
                }
            else:
                return {"error": f"Adzuna API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Adzuna API request failed: {str(e)}"}
    
    def search_jsearch_jobs(self, query, location="United States", num_pages=1):
        """Search jobs using JSearch API via RapidAPI"""
        if not self.rapidapi_key:
            return {"error": "RapidAPI key not configured"}
        
        try:
            url = "https://jsearch.p.rapidapi.com/search"
            
            querystring = {
                "query": f"{query} in {location}",
                "page": "1",
                "num_pages": str(num_pages)
            }
            
            headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                jobs = []
                
                for job in data.get('data', []):
                    jobs.append({
                        'title': job.get('job_title', ''),
                        'company': job.get('employer_name', ''),
                        'location': job.get('job_city', '') + ', ' + job.get('job_state', ''),
                        'salary_min': job.get('job_min_salary'),
                        'salary_max': job.get('job_max_salary'),
                        'description': job.get('job_description', '')[:500] + '...',
                        'url': job.get('job_apply_link', ''),
                        'employment_type': job.get('job_employment_type', ''),
                        'source': 'JSearch'
                    })
                
                return {
                    'jobs': jobs,
                    'total_count': len(jobs),
                    'source': 'JSearch API'
                }
            else:
                return {"error": f"JSearch API error: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"JSearch API request failed: {str(e)}"}
    
    def search_github_jobs(self, description, location=""):
        """Search GitHub Jobs (Note: GitHub Jobs API was discontinued, this is a fallback)"""
        # GitHub Jobs API was discontinued in May 2021
        # This is a placeholder for alternative job sources
        return {
            "jobs": [],
            "message": "GitHub Jobs API discontinued. Using alternative sources.",
            "source": "GitHub (Discontinued)"
        }
    
    def get_job_recommendations(self, skills, role, location="United States", experience_level="mid"):
        """Get comprehensive job recommendations from multiple sources"""
        
        # Create search queries based on skills and role
        primary_query = f"{role} {' '.join(skills[:3])}"
        
        all_jobs = []
        sources_used = []
        
        # Try Adzuna first
        adzuna_results = self.search_adzuna_jobs(primary_query, location, 5)
        if 'jobs' in adzuna_results:
            all_jobs.extend(adzuna_results['jobs'])
            sources_used.append('Adzuna')
        
        # Try JSearch
        jsearch_results = self.search_jsearch_jobs(primary_query, location, 1)
        if 'jobs' in jsearch_results:
            all_jobs.extend(jsearch_results['jobs'])
            sources_used.append('JSearch')
        
        # Filter and rank jobs based on skills match
        ranked_jobs = self.rank_jobs_by_skills(all_jobs, skills, role)
        
        return {
            'recommended_jobs': ranked_jobs[:10],  # Top 10 recommendations
            'total_found': len(all_jobs),
            'sources_used': sources_used,
            'search_criteria': {
                'role': role,
                'skills': skills,
                'location': location,
                'experience_level': experience_level
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def rank_jobs_by_skills(self, jobs, skills, target_role):
        """Rank jobs based on skill match and relevance"""
        
        for job in jobs:
            score = 0
            job_text = (job.get('title', '') + ' ' + job.get('description', '')).lower()
            
            # Score based on skill matches
            for skill in skills:
                if skill.lower() in job_text:
                    score += 10
            
            # Score based on role match
            if target_role.lower() in job.get('title', '').lower():
                score += 20
            
            # Score based on company reputation (basic heuristic)
            company = job.get('company', '').lower()
            if any(tech_company in company for tech_company in ['google', 'microsoft', 'amazon', 'apple', 'meta', 'netflix']):
                score += 15
            
            job['match_score'] = score
            job['skill_matches'] = [skill for skill in skills if skill.lower() in job_text]
        
        # Sort by match score
        return sorted(jobs, key=lambda x: x.get('match_score', 0), reverse=True)
    
    def get_salary_insights(self, role, location="United States"):
        """Get salary insights for a specific role and location"""
        
        # This would typically use salary APIs like Glassdoor, PayScale, etc.
        # For now, providing estimated ranges based on common data
        
        salary_data = {
            'Software Engineer': {'min': 70000, 'max': 150000, 'median': 95000},
            'Senior Software Engineer': {'min': 100000, 'max': 200000, 'median': 135000},
            'Frontend Developer': {'min': 65000, 'max': 130000, 'median': 85000},
            'Backend Developer': {'min': 75000, 'max': 140000, 'median': 100000},
            'Full Stack Developer': {'min': 70000, 'max': 145000, 'median': 95000},
            'Data Scientist': {'min': 80000, 'max': 160000, 'median': 110000},
            'DevOps Engineer': {'min': 85000, 'max': 155000, 'median': 115000}
        }
        
        base_salary = salary_data.get(role, {'min': 60000, 'max': 120000, 'median': 80000})
        
        return {
            'role': role,
            'location': location,
            'salary_range': base_salary,
            'currency': 'USD',
            'note': 'Estimated ranges based on market data',
            'last_updated': datetime.now().isoformat()
        }

def main():
    """Test the job API integration"""
    job_api = JobAPIIntegrator()
    
    # Test job search
    print("Testing Job API Integration...")
    print("=" * 50)
    
    # Example search
    skills = ['Python', 'Django', 'React', 'AWS']
    role = 'Software Engineer'
    
    results = job_api.get_job_recommendations(skills, role)
    
    print(f"Found {results['total_found']} jobs from {len(results['sources_used'])} sources")
    print(f"Sources: {', '.join(results['sources_used'])}")
    print("\nTop 3 Recommendations:")
    
    for i, job in enumerate(results['recommended_jobs'][:3], 1):
        print(f"\n{i}. {job['title']} at {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Match Score: {job['match_score']}")
        print(f"   Skills Match: {', '.join(job['skill_matches'])}")
        if job.get('salary_min') and job.get('salary_max'):
            print(f"   Salary: ${job['salary_min']:,} - ${job['salary_max']:,}")
    
    # Test salary insights
    salary_info = job_api.get_salary_insights(role)
    print(f"\nSalary Insights for {role}:")
    print(f"Range: ${salary_info['salary_range']['min']:,} - ${salary_info['salary_range']['max']:,}")
    print(f"Median: ${salary_info['salary_range']['median']:,}")

if __name__ == "__main__":
    main()