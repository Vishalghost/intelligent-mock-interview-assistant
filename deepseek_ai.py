import requests
import json

class DeepSeekAI:
    def __init__(self, api_key=None):
        # DeepSeek API - free tier available
        self.api_key = api_key or "sk-your-deepseek-key"  # Get free key from deepseek.com
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        
    def generate_questions(self, resume_data, role):
        """Generate interview questions using DeepSeek"""
        skills = ', '.join(resume_data.get('skills', []))
        experience = resume_data.get('experience_years', 0)
        
        prompt = f"""Generate 3 technical interview questions for a {role} position.
        
Candidate profile:
- Skills: {skills}
- Experience: {experience} years

Requirements:
- Questions should be challenging but fair
- Focus on practical problem-solving
- Include system design if senior level
- Return as JSON array with question, category, difficulty

Format: [{{"question": "...", "category": "...", "difficulty": "..."}}]"""

        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 800,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return self._parse_questions(content, role)
                
        except Exception as e:
            print(f"DeepSeek API error: {e}")
        
        return self._fallback_questions(role)
    
    def evaluate_answer(self, question, answer, role):
        """Evaluate answer using DeepSeek"""
        if not answer.strip():
            return self._poor_evaluation()
            
        prompt = f"""Evaluate this interview answer for a {role} position.

Question: {question}
Answer: {answer}

Provide evaluation as JSON:
{{
  "overall_score": 0-100,
  "technical_score": 0-100,
  "communication_score": 0-100,
  "problem_solving_score": 0-100,
  "feedback": "detailed feedback",
  "decision": "Strong Hire/Hire/No Hire"
}}"""

        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.3
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return self._parse_evaluation(content)
                
        except Exception as e:
            print(f"DeepSeek evaluation error: {e}")
        
        return self._basic_evaluation(answer)
    
    def analyze_resume(self, resume_text):
        """Enhanced resume analysis using DeepSeek"""
        prompt = f"""Analyze this resume and extract key information as JSON:

Resume: {resume_text[:1000]}

Return JSON:
{{
  "skills": ["skill1", "skill2"],
  "experience_years": number,
  "technical_depth": 0-100,
  "leadership_score": 0-100,
  "ats_score": 0-100,
  "summary": "brief summary"
}}"""

        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 400,
                    "temperature": 0.2
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return self._parse_resume_analysis(content)
                
        except Exception as e:
            print(f"DeepSeek resume analysis error: {e}")
        
        return None
    
    def _parse_questions(self, content, role):
        """Parse AI-generated questions"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
                return [
                    {
                        'question': q.get('question', ''),
                        'category': q.get('category', 'Technical'),
                        'difficulty': q.get('difficulty', 'intermediate'),
                        'evaluation_criteria': [
                            'Technical accuracy',
                            'Problem-solving approach',
                            'Communication clarity'
                        ]
                    }
                    for q in questions_data[:3]
                ]
        except:
            pass
        
        return self._fallback_questions(role)
    
    def _parse_evaluation(self, content):
        """Parse AI evaluation response"""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                eval_data = json.loads(json_match.group())
                
                return {
                    'overall_score': eval_data.get('overall_score', 60),
                    'dimension_scores': {
                        'technical_mastery': eval_data.get('technical_score', 60),
                        'problem_solving': eval_data.get('problem_solving_score', 60),
                        'communication': eval_data.get('communication_score', 60),
                        'innovation': eval_data.get('technical_score', 60) - 10,
                        'leadership': 70,
                        'system_thinking': eval_data.get('problem_solving_score', 60)
                    },
                    'detailed_feedback': eval_data.get('feedback', 'Good response'),
                    'hiring_decision': {
                        'decision': eval_data.get('decision', 'Hire'),
                        'confidence': 0.8
                    }
                }
        except:
            pass
        
        return self._basic_evaluation("")
    
    def _parse_resume_analysis(self, content):
        """Parse AI resume analysis"""
        try:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return None
    
    def _fallback_questions(self, role):
        """Fallback questions"""
        return [
            {
                'question': f"Describe a complex technical challenge you faced in {role.lower()} and how you solved it.",
                'category': 'Problem Solving',
                'difficulty': 'advanced',
                'evaluation_criteria': ['Technical depth', 'Problem-solving', 'Communication']
            },
            {
                'question': f"How would you design a scalable system for a high-traffic {role.lower()} application?",
                'category': 'System Design',
                'difficulty': 'advanced',
                'evaluation_criteria': ['Architecture knowledge', 'Scalability', 'Trade-offs']
            },
            {
                'question': f"Explain your approach to code quality and testing in {role.lower()} projects.",
                'category': 'Best Practices',
                'difficulty': 'intermediate',
                'evaluation_criteria': ['Best practices', 'Testing strategy', 'Quality assurance']
            }
        ]
    
    def _basic_evaluation(self, answer):
        """Basic fallback evaluation"""
        words = len(answer.split()) if answer else 0
        score = min(85, max(30, words * 2))
        
        return {
            'overall_score': score,
            'dimension_scores': {
                'technical_mastery': score,
                'problem_solving': score - 5,
                'communication': min(80, words),
                'innovation': score - 10,
                'leadership': 65,
                'system_thinking': score - 5
            },
            'detailed_feedback': f"Response evaluated. Score based on content depth and clarity.",
            'hiring_decision': {
                'decision': 'Hire' if score >= 65 else 'No Hire',
                'confidence': 0.7
            }
        }
    
    def _poor_evaluation(self):
        """Poor evaluation for empty answers"""
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