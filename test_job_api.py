#!/usr/bin/env python3
"""
Test Job API Integration
"""

from job_api_integration import JobAPIIntegrator

def test_job_api():
    print("Testing Job API Integration...")
    print("=" * 50)
    
    job_api = JobAPIIntegrator()
    
    # Test with sample skills and role
    skills = ['Python', 'Django', 'React', 'JavaScript', 'AWS']
    role = 'Software Engineer'
    location = 'United States'
    
    print(f"Searching for: {role}")
    print(f"Skills: {', '.join(skills)}")
    print(f"Location: {location}")
    print()
    
    # Get job recommendations
    results = job_api.get_job_recommendations(skills, role, location)
    
    if 'error' in results:
        print(f"[ERROR] {results['error']}")
        print("\n[INFO] To enable real job API integration:")
        print("1. Sign up for Adzuna API: https://developer.adzuna.com/")
        print("2. Get RapidAPI key: https://rapidapi.com/")
        print("3. Add API keys to .env file:")
        print("   ADZUNA_APP_ID=your_app_id")
        print("   ADZUNA_API_KEY=your_api_key")
        print("   RAPIDAPI_KEY=your_rapidapi_key")
        return
    
    print(f"[SUCCESS] Found {results['total_found']} jobs from {len(results['sources_used'])} sources")
    print(f"[SOURCES] {', '.join(results['sources_used'])}")
    print()
    
    # Display top recommendations
    print("[TOP JOBS] Job Recommendations:")
    print("-" * 40)
    
    for i, job in enumerate(results['recommended_jobs'][:5], 1):
        print(f"{i}. {job['title']} at {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Match Score: {job['match_score']}")
        
        if job.get('skill_matches'):
            print(f"   Skills Match: {', '.join(job['skill_matches'])}")
        
        if job.get('salary_min') and job.get('salary_max'):
            print(f"   Salary: ${job['salary_min']:,} - ${job['salary_max']:,}")
        
        if job.get('url'):
            print(f"   Apply: {job['url'][:60]}...")
        
        print()
    
    # Get salary insights
    salary_info = job_api.get_salary_insights(role, location)
    print("[SALARY] Salary Insights:")
    print("-" * 20)
    print(f"Role: {salary_info['role']}")
    print(f"Range: ${salary_info['salary_range']['min']:,} - ${salary_info['salary_range']['max']:,}")
    print(f"Median: ${salary_info['salary_range']['median']:,}")
    print()
    
    print("[SUCCESS] Job API Integration Test Complete!")

if __name__ == "__main__":
    test_job_api()