import requests
import json
import hashlib
import os
import re
from typing import Dict, List, Optional, Any

class OptimizedDeepSeekAI:
    def __init__(self, api_key=None):
        # Security: Use environment variables for API keys only
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            print("Warning: DEEPSEEK_API_KEY environment variable not set")
            self.use_ai = False
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.cache_dir = "ai_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        self.use_ai = True  # Toggle to save tokens
        self.model = "deepseek-chat"  # Model name as variable for easy changes
        
        # Token counters for monitoring
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        
    def generate_questions(self, resume_data: Dict, role: str) -> List[Dict]:
        """Generate interview questions with optimized token usage"""
        if not self.use_ai:
            return self._fallback_questions(role)
            
        # Create a more specific cache key
        exp_level = resume_data.get('experience_years', 0)
        skills_hash = hashlib.md5(str(resume_data.get('skills', [])).encode()).hexdigest()[:8]
        cache_key = f"q_{role}_{exp_level}_{skills_hash}"
        
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        # Extract key skills for more targeted questions
        top_skills = resume_data.get('skills', [])[:3]  # Top 3 skills only
        skills_text = ", ".join(top_skills) if top_skills else "general technical"
        
        # Ultra-efficient prompt (under 40 tokens)
        prompt = (
            f"Role: {role}. Exp: {exp_level}y. Skills: {skills_text}. "
            f"Generate 3 interview questions as JSON: ["
            f'{{"q":"question","cat":"category","diff":"difficulty"}}]'
        )
        
        try:
            response = self._api_call(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,  # Increased for 5 questions
                temperature=0.7
            )
            
            if response:
                content = response['choices'][0]['message']['content']
                questions = self._parse_questions(content, role)
                if questions:
                    self._set_cache(cache_key, questions)
                    return questions
                    
        except Exception as e:
            print(f"Question generation error: {e}")
        
        return self._fallback_questions(role)
    
    def evaluate_answer(self, question: str, answer: str, role: str) -> Dict:
        """Smart evaluation with token optimization"""
        if not answer.strip():
            return self._poor_evaluation()
            
        # Determine if answer is substantial enough for AI evaluation
        word_count = len(answer.split())
        if not self.use_ai or word_count < 30:  # Reduced threshold from 50 to 30
            return self._basic_evaluation(answer)
            
        # Create cache key for similar answers to same question
        answer_hash = hashlib.md5(answer[:100].encode()).hexdigest()[:10]
        question_hash = hashlib.md5(question[:50].encode()).hexdigest()[:6]
        cache_key = f"eval_{role}_{question_hash}_{answer_hash}"
        
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        # Extract question category for better evaluation context
        category = "Technical"  # Default
        if "behavior" in question.lower() or "experience" in question.lower():
            category = "Behavioral"
        elif "system" in question.lower() or "design" in question.lower():
            category = "System Design"
            
        # Efficient prompt (under 35 tokens)
        prompt = (
            f"Evaluate this {category} answer for {role} role. "
            f"Answer: {answer[:150]}... "  # First 150 chars only
            f"JSON: {{'score':X,'feedback':'brief','decision':'Hire/No Hire'}}"
        )
        
        try:
            response = self._api_call(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=60,  # Reduced from original 80
                temperature=0.3
            )
            
            if response:
                content = response['choices'][0]['message']['content']
                evaluation = self._parse_evaluation(content, answer)
                if evaluation:
                    self._set_cache(cache_key, evaluation)
                    return evaluation
                    
        except Exception as e:
            print(f"Evaluation error: {e}")
        
        return self._basic_evaluation(answer)
    
    def analyze_resume(self, resume_text: str) -> Optional[Dict]:
        """Complete resume analysis using DeepSeek API"""
        if not self.use_ai or not resume_text.strip():
            return None
            
        # Create hash of key resume content for caching
        text_hash = hashlib.md5(resume_text[:500].encode()).hexdigest()[:10]
        cache_key = f"resume_full_{text_hash}"
        
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        # Enhanced prompt for comprehensive analysis
        prompt = (
            f"Analyze this resume comprehensively: {resume_text[:800]}\n\n"
            f"Return JSON with: {{"
            f'"name":"candidate name",'
            f'"email":"email",'
            f'"skills":["skill1","skill2"],'
            f'"experience_years":X,'
            f'"education":["degree info"],'
            f'"certifications":["cert1"],'
            f'"ats_score":X,'
            f'"technical_depth":X,'
            f'"leadership_score":X'
            f"}}"
        )
        
        try:
            response = self._api_call(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.2
            )
            
            if response:
                content = response['choices'][0]['message']['content']
                analysis = self._parse_resume_analysis(content)
                
                if analysis:
                    # Ensure required fields exist
                    analysis.setdefault('name', 'Candidate')
                    analysis.setdefault('skills', [])
                    analysis.setdefault('experience_years', 0)
                    analysis.setdefault('ats_score', 50)
                    analysis.setdefault('technical_depth', 40)
                    analysis.setdefault('leadership_score', 30)
                    
                    self._set_cache(cache_key, analysis)
                    return analysis
                    
        except Exception as e:
            print(f"Resume analysis error: {e}")
        
        return None
    
    def _api_call(self, messages: List[Dict], max_tokens: int, temperature: float) -> Optional[Dict]:
        """Centralized API call with error handling and token tracking"""
        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}", 
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": False
                },
                timeout=15  # Add timeout to prevent hanging
            )
            
            if response.status_code == 200:
                result = response.json()
                # Track token usage
                if 'usage' in result:
                    self.total_input_tokens += result['usage'].get('prompt_tokens', 0)
                    self.total_output_tokens += result['usage'].get('completion_tokens', 0)
                return result
            else:
                print(f"API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print("API request timed out")
            return None
        except Exception as e:
            print(f"API call failed: {e}")
            return None
    
    def _extract_education(self, text: str) -> List[str]:
        """Local extraction of education info to save tokens"""
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college']
        education = []
        
        for line in text.split('\n'):
            if any(keyword in line.lower() for keyword in education_keywords):
                education.append(line.strip())
                if len(education) >= 2:  # Limit to top 2 education entries
                    break
                    
        return education
    
    def _extract_experience(self, text: str) -> int:
        """Local estimation of experience years to save tokens"""
        # Look for year patterns like "2015-2019" or "5 years"
        year_matches = re.findall(r'(\d{4})\s*[-–]\s*(\d{4})', text)
        year_count_matches = re.findall(r'(\d+)\s+(year|yr)', text, re.IGNORECASE)
        
        experience = 0
        
        # Calculate experience from year ranges
        if year_matches:
            for start, end in year_matches:
                try:
                    experience += (int(end) - int(start))
                except:
                    pass
        
        # Add explicit year mentions
        if year_count_matches:
            for years, _ in year_count_matches:
                try:
                    experience += int(years)
                except:
                    pass
        
        # If we found multiple experiences, take the maximum
        if year_matches or year_count_matches:
            return min(30, experience)  # Cap at 30 years
        
        # Fallback: estimate based on keyword presence
        seniority_keywords = ['senior', 'lead', 'principal', 'manager', 'director', 'head of']
        if any(keyword in text.lower() for keyword in seniority_keywords):
            return 5  # Default for senior roles
            
        return 2  # Default for other roles
    
    def _parse_questions(self, content: str, role: str) -> List[Dict]:
        """Parse questions from API response with robust error handling"""
        try:
            # Find JSON pattern in response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
                return [
                    {
                        'question': q.get('q', q.get('question', '')),
                        'category': q.get('cat', q.get('category', 'Technical')),
                        'difficulty': q.get('diff', q.get('difficulty', 'intermediate')),
                        'evaluation_criteria': ['Technical accuracy', 'Problem-solving', 'Communication']
                    }
                    for q in questions_data[:3]  # Limit to 3 questions
                ]
        except json.JSONDecodeError:
            # Fallback: extract questions using regex if JSON parsing fails
            questions = re.findall(r'"q":"([^"]+)"', content)
            if questions:
                return [
                    {
                        'question': q,
                        'category': 'Technical',
                        'difficulty': 'intermediate',
                        'evaluation_criteria': ['Technical accuracy', 'Problem-solving', 'Communication']
                    }
                    for q in questions[:3]
                ]
        except Exception as e:
            print(f"Question parsing error: {e}")
            
        return self._fallback_questions(role)
    
    def _parse_evaluation(self, content: str, answer: str) -> Dict:
        """Parse evaluation from API response"""
        try:
            # Find JSON pattern in response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                eval_data = json.loads(json_match.group())
                score = min(100, max(0, eval_data.get('score', 60)))  # Ensure score is between 0-100
                
                return {
                    'overall_score': score,
                    'dimension_scores': {
                        'technical_mastery': score,
                        'problem_solving': max(0, score - 5),
                        'communication': min(100, len(answer.split()) * 2),  # Scale with answer length
                        'innovation': max(0, score - 10),
                        'leadership': max(0, score - 15),
                        'system_thinking': max(0, score - 5)
                    },
                    'detailed_feedback': eval_data.get('feedback', f"Score: {score}/100"),
                    'hiring_decision': {
                        'decision': eval_data.get('decision', 'Hire' if score >= 70 else 'No Hire'),
                        'confidence': min(1.0, max(0.1, score / 100))  # Scale confidence with score
                    }
                }
        except Exception as e:
            print(f"Evaluation parsing error: {e}")
            
        return self._basic_evaluation(answer)
    
    def _parse_resume_analysis(self, content: str) -> Optional[Dict]:
        """Parse resume analysis from API response with enhanced extraction"""
        try:
            # Find JSON pattern in response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                # Ensure skills is properly formatted
                if 'skills' in data and isinstance(data['skills'], list):
                    # Convert to enhanced skills format
                    data['skills'] = {
                        'all_skills': data['skills'],
                        'total_count': len(data['skills']),
                        'technical_by_category': {
                            'programming_languages': [s for s in data['skills'] if s.lower() in ['python', 'java', 'javascript', 'go', 'rust', 'c++']],
                            'web_technologies': [s for s in data['skills'] if s.lower() in ['react', 'angular', 'vue', 'django', 'flask']],
                            'databases': [s for s in data['skills'] if s.lower() in ['mysql', 'postgresql', 'mongodb', 'redis']],
                            'cloud_platforms': [s for s in data['skills'] if s.lower() in ['aws', 'azure', 'gcp']],
                            'devops_tools': [s for s in data['skills'] if s.lower() in ['docker', 'kubernetes', 'jenkins']]
                        },
                        'soft_skills': [s for s in data['skills'] if s.lower() in ['leadership', 'communication', 'teamwork']]
                    }
                
                return data
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            # Try to extract individual fields
            name_match = re.search(r'"name"\s*:\s*"([^"]+)"', content)
            skills_match = re.search(r'"skills"\s*:\s*\[([^\]]+)\]', content)
            exp_match = re.search(r'"experience_years"\s*:\s*(\d+)', content)
            
            if any([name_match, skills_match, exp_match]):
                result = {}
                if name_match:
                    result['name'] = name_match.group(1)
                if skills_match:
                    skills = [s.strip('"').strip() for s in skills_match.group(1).split(',')]
                    result['skills'] = {'all_skills': skills, 'total_count': len(skills)}
                if exp_match:
                    result['experience_years'] = int(exp_match.group(1))
                return result
                
        except Exception as e:
            print(f"Resume analysis parsing error: {e}")
            
        return None
    
    def _get_cache(self, key: str) -> Any:
        """Retrieve item from cache"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Cache read error: {e}")
        return None
    
    def _set_cache(self, key: str, data: Any) -> None:
        """Store item in cache"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Cache write error: {e}")
    
    def toggle_ai(self, enabled: bool = True) -> None:
        """Toggle AI usage to save tokens"""
        self.use_ai = enabled
        print(f"AI: {'ON' if enabled else 'OFF'} - Token saving mode activated!")
    
    def get_token_usage(self) -> Dict[str, int]:
        """Get current token usage statistics"""
        return {
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens
        }
    
    def _fallback_questions(self, role: str) -> List[Dict]:
        """Fallback questions when API is unavailable"""
        return [
            {
                'question': f"Describe a challenging {role.lower()} project you've worked on.",
                'category': 'Technical',
                'difficulty': 'intermediate',
                'evaluation_criteria': ['Technical depth', 'Problem-solving', 'Communication']
            },
            {
                'question': f"How do you ensure code quality in {role.lower()} development?",
                'category': 'Best Practices',
                'difficulty': 'intermediate',
                'evaluation_criteria': ['Best practices', 'Testing', 'Quality assurance']
            },
            {
                'question': f"Explain your approach to system design for {role.lower()} applications.",
                'category': 'System Design',
                'difficulty': 'advanced',
                'evaluation_criteria': ['Architecture', 'Scalability', 'Trade-offs']
            }
        ]
    
    def _basic_evaluation(self, answer: str) -> Dict:
        """Basic evaluation when AI is not used"""
        words = len(answer.split()) if answer else 0
        score = min(85, max(30, words * 1.2))  # Adjusted scoring algorithm
        
        return {
            'overall_score': int(score),
            'dimension_scores': {
                'technical_mastery': int(score),
                'problem_solving': max(0, int(score - 5)),
                'communication': min(100, words * 2),
                'innovation': max(0, int(score - 10)),
                'leadership': max(0, int(score - 15)),
                'system_thinking': max(0, int(score - 5))
            },
            'detailed_feedback': "AI evaluation not available. Consider adding more technical details." if words > 10 else "Response too short for proper evaluation.",
            'hiring_decision': {
                'decision': 'Hire' if score >= 65 else 'No Hire',
                'confidence': min(0.9, max(0.5, score / 100))  # Adjusted confidence calculation
            }
        }
    
    def _poor_evaluation(self) -> Dict:
        """Evaluation for empty answers"""
        return {
            'overall_score': 20,
            'dimension_scores': {
                'technical_mastery': 20, 
                'problem_solving': 20, 
                'communication': 10,
                'innovation': 20, 
                'leadership': 30, 
                'system_thinking': 20
            },
            'detailed_feedback': "No response provided. Please provide a detailed answer.",
            'hiring_decision': {
                'decision': 'No Hire', 
                'confidence': 0.9
            }
        }


# Example usage
if __name__ == "__main__":
    ai = OptimizedDeepSeekAI()
    
    # Example resume data
    resume_data = {
        'experience_years': 5,
        'skills': ['Python', 'Django', 'React', 'AWS', 'Docker']
    }
    
    # Generate questions
    questions = ai.generate_questions(resume_data, "Backend Developer")
    print("Generated Questions:", questions)
    
    # Evaluate an answer
    evaluation = ai.evaluate_answer(
        questions[0]['question'], 
        "I implemented a scalable microservices architecture using Docker and Kubernetes...",
        "Backend Developer"
    )
    print("Evaluation:", evaluation)
    
    # Check token usage
    print("Token Usage:", ai.get_token_usage())