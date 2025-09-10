class DomainMatcher:
    def __init__(self):
        self.domain_skills = {
            'Frontend Development': ['react', 'vue', 'angular', 'javascript', 'typescript', 'html', 'css', 'sass', 'webpack'],
            'Backend Development': ['python', 'java', 'node.js', 'express', 'django', 'flask', 'spring', 'api', 'rest'],
            'Full Stack Development': ['react', 'node.js', 'python', 'javascript', 'mongodb', 'postgresql', 'api'],
            'Data Science': ['python', 'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'sql', 'statistics'],
            'Machine Learning': ['tensorflow', 'pytorch', 'scikit-learn', 'python', 'deep learning', 'neural networks'],
            'DevOps Engineering': ['docker', 'kubernetes', 'aws', 'jenkins', 'terraform', 'ansible', 'linux', 'ci/cd'],
            'Mobile Development': ['react native', 'flutter', 'swift', 'kotlin', 'ios', 'android', 'mobile'],
            'Cloud Engineering': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'serverless'],
            'Cybersecurity': ['security', 'penetration testing', 'cryptography', 'network security', 'compliance'],
            'Product Management': ['product strategy', 'roadmap', 'agile', 'scrum', 'analytics', 'user research']
        }
    
    def determine_best_fit_domain(self, candidate_data):
        skills = candidate_data.get('skills', [])
        if isinstance(skills, dict):
            all_skills = []
            for category_skills in skills.values():
                if isinstance(category_skills, list):
                    all_skills.extend(category_skills)
            skills = all_skills
        
        # Normalize skills to lowercase
        normalized_skills = [skill.lower() for skill in skills]
        
        domain_scores = {}
        for domain, domain_skills in self.domain_skills.items():
            score = 0
            for skill in normalized_skills:
                for domain_skill in domain_skills:
                    if domain_skill.lower() in skill or skill in domain_skill.lower():
                        score += 1
            domain_scores[domain] = score
        
        # Get top 3 domains
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate confidence based on experience and ATS score
        experience = candidate_data.get('experience_years', 0)
        ats_score = candidate_data.get('ats_score', 0)
        
        confidence_multiplier = min(1.0, (experience * 0.1 + ats_score * 0.01))
        
        best_fit = {
            'primary_domain': sorted_domains[0][0] if sorted_domains[0][1] > 0 else 'General Software Development',
            'confidence': min(95, max(30, sorted_domains[0][1] * 15 * confidence_multiplier)),
            'alternative_domains': [domain for domain, score in sorted_domains[1:4] if score > 0],
            'skill_match_count': sorted_domains[0][1] if sorted_domains else 0,
            'recommended_level': self._determine_level(experience, ats_score)
        }
        
        return best_fit
    
    def _determine_level(self, experience, ats_score):
        if experience >= 8 or ats_score >= 85:
            return 'Senior/Lead'
        elif experience >= 4 or ats_score >= 70:
            return 'Mid-Level'
        elif experience >= 2 or ats_score >= 55:
            return 'Junior'
        else:
            return 'Entry-Level'