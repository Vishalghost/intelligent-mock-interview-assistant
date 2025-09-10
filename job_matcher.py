import requests
from typing import List, Dict

class JobMatcher:
    def __init__(self):
        self.job_apis = {
            'github': 'https://jobs.github.com/positions.json',
            'remoteok': 'https://remoteok.io/api'
        }
    
    def fetch_jobs(self, domain: str, skills: List[str], min_score: int = 60) -> List[Dict]:
        """Fetch relevant job postings based on candidate profile"""
        jobs = []
        
        # Fetch from GitHub Jobs (if available)
        try:
            jobs.extend(self._fetch_github_jobs(domain, skills))
        except:
            pass
        
        # Fetch from RemoteOK
        try:
            jobs.extend(self._fetch_remoteok_jobs(domain, skills))
        except:
            pass
        
        # Filter and rank jobs
        return self._rank_jobs(jobs, skills, min_score)
    
    def _fetch_github_jobs(self, domain: str, skills: List[str]) -> List[Dict]:
        """Fetch jobs from GitHub Jobs API"""
        params = {
            'description': domain.lower(),
            'location': 'remote'
        }
        
        response = requests.get(self.job_apis['github'], params=params, timeout=10)
        if response.status_code == 200:
            return response.json()[:10]  # Limit to 10 jobs
        return []
    
    def _fetch_remoteok_jobs(self, domain: str, skills: List[str]) -> List[Dict]:
        """Fetch jobs from RemoteOK API"""
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(self.job_apis['remoteok'], headers=headers, timeout=10)
        
        if response.status_code == 200:
            jobs = response.json()
            # Filter relevant jobs
            relevant_jobs = []
            for job in jobs[:20]:  # Check first 20 jobs
                if isinstance(job, dict) and any(skill.lower() in str(job).lower() for skill in skills):
                    relevant_jobs.append(job)
                if len(relevant_jobs) >= 5:
                    break
            return relevant_jobs
        return []
    
    def _rank_jobs(self, jobs: List[Dict], skills: List[str], min_score: int) -> List[Dict]:
        """Rank jobs based on skill match"""
        ranked_jobs = []
        
        for job in jobs:
            job_text = str(job).lower()
            skill_matches = sum(1 for skill in skills if skill.lower() in job_text)
            match_score = (skill_matches / len(skills)) * 100 if skills else 0
            
            if match_score >= min_score:
                job['match_score'] = match_score
                ranked_jobs.append(job)
        
        return sorted(ranked_jobs, key=lambda x: x.get('match_score', 0), reverse=True)[:5]