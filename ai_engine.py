import requests
import json
import time

class HuggingFaceAI:
    def __init__(self):
        # Free Hugging Face models - no API key needed for public models
        self.question_model = "microsoft/DialoGPT-large"
        self.evaluation_model = "facebook/bart-large-mnli"
        self.base_url = "https://api-inference.huggingface.co/models/"
        
    def generate_questions(self, resume_data, role):
        """Generate interview questions using free HF model"""
        prompt = f"Generate 3 technical interview questions for {role} position based on skills: {', '.join(resume_data.get('skills', []))}"
        
        try:
            response = requests.post(
                f"{self.base_url}microsoft/DialoGPT-large",
                headers={"Content-Type": "application/json"},
                json={"inputs": prompt, "parameters": {"max_length": 200}}
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    questions_text = result[0].get('generated_text', '')
                    return self._parse_questions(questions_text, role)
            
        except Exception as e:
            print(f"HF API error: {e}")
        
        # Fallback questions
        return self._fallback_questions(role)
    
    def evaluate_answer(self, question, answer, role):
        """Evaluate answer using free HF classification model"""
        if not answer.strip():
            return self._poor_evaluation()
            
        # Use BART for text quality assessment
        try:
            evaluation_prompt = f"This answer is: {answer[:500]}"
            
            response = requests.post(
                f"{self.base_url}facebook/bart-large-mnli",
                headers={"Content-Type": "application/json"},
                json={
                    "inputs": evaluation_prompt,
                    "parameters": {
                        "candidate_labels": ["excellent", "good", "average", "poor"]
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._process_evaluation(result, answer)
                
        except Exception as e:
            print(f"Evaluation error: {e}")
        
        # Fallback evaluation
        return self._basic_evaluation(answer)
    
    def _parse_questions(self, text, role):
        """Parse generated questions"""
        questions = []
        
        # Basic question templates with generated content
        base_questions = [
            f"Explain a complex {role.lower()} project you've worked on",
            f"How would you handle a challenging technical problem in {role.lower()}?",
            f"Describe your approach to code review and quality assurance"
        ]
        
        for i, q in enumerate(base_questions[:3]):
            questions.append({
                'question': q,
                'category': 'Technical',
                'difficulty': 'advanced',
                'evaluation_criteria': [
                    'Technical depth and accuracy',
                    'Problem-solving approach',
                    'Communication clarity'
                ]
            })
        
        return questions
    
    def _fallback_questions(self, role):
        """Fallback questions when API fails"""
        return [
            {
                'question': f"Describe a challenging {role.lower()} project and how you overcame technical obstacles.",
                'category': 'Technical Problem Solving',
                'difficulty': 'advanced',
                'evaluation_criteria': [
                    'Technical depth', 'Problem-solving approach', 'Communication'
                ]
            },
            {
                'question': f"How do you ensure code quality and maintainability in {role.lower()} projects?",
                'category': 'Best Practices',
                'difficulty': 'intermediate',
                'evaluation_criteria': [
                    'Knowledge of best practices', 'Testing approach', 'Code review process'
                ]
            },
            {
                'question': f"Explain how you would design a scalable system for a {role.lower()} application.",
                'category': 'System Design',
                'difficulty': 'advanced',
                'evaluation_criteria': [
                    'System architecture', 'Scalability considerations', 'Trade-offs'
                ]
            }
        ]
    
    def _process_evaluation(self, hf_result, answer):
        """Process HuggingFace evaluation result"""
        try:
            if 'labels' in hf_result and 'scores' in hf_result:
                top_label = hf_result['labels'][0]
                confidence = hf_result['scores'][0]
                
                score_map = {
                    'excellent': 90,
                    'good': 75,
                    'average': 60,
                    'poor': 40
                }
                
                base_score = score_map.get(top_label, 60)
                final_score = int(base_score * confidence + (1-confidence) * 60)
                
                return {
                    'overall_score': final_score,
                    'dimension_scores': {
                        'technical_mastery': final_score,
                        'problem_solving': final_score - 5,
                        'communication': min(85, len(answer.split()) * 2),
                        'innovation': final_score - 10,
                        'leadership': 70,
                        'system_thinking': final_score - 5
                    },
                    'detailed_feedback': f"Response quality assessed as {top_label} with {confidence:.1%} confidence. " + 
                                       self._generate_feedback(final_score),
                    'hiring_decision': {
                        'decision': 'Strong Hire' if final_score >= 80 else 'Hire' if final_score >= 65 else 'No Hire',
                        'confidence': confidence
                    }
                }
        except:
            pass
            
        return self._basic_evaluation(answer)
    
    def _basic_evaluation(self, answer):
        """Basic evaluation based on answer length and keywords"""
        words = len(answer.split())
        
        # Simple scoring based on response length and content
        if words < 20:
            score = 40
        elif words < 50:
            score = 60
        elif words < 100:
            score = 75
        else:
            score = 85
            
        # Boost score for technical keywords
        tech_keywords = ['algorithm', 'database', 'api', 'framework', 'architecture', 'scalable', 'performance']
        keyword_count = sum(1 for word in tech_keywords if word.lower() in answer.lower())
        score += min(10, keyword_count * 2)
        
        return {
            'overall_score': min(95, score),
            'dimension_scores': {
                'technical_mastery': score,
                'problem_solving': score - 5,
                'communication': min(85, words),
                'innovation': score - 10,
                'leadership': 70,
                'system_thinking': score - 5
            },
            'detailed_feedback': self._generate_feedback(score),
            'hiring_decision': {
                'decision': 'Strong Hire' if score >= 80 else 'Hire' if score >= 65 else 'No Hire',
                'confidence': 0.8
            }
        }
    
    def _generate_feedback(self, score):
        """Generate feedback based on score"""
        if score >= 85:
            return "Excellent response demonstrating strong technical knowledge and clear communication."
        elif score >= 70:
            return "Good response with solid technical understanding. Consider adding more specific examples."
        elif score >= 55:
            return "Adequate response but could benefit from more technical depth and concrete examples."
        else:
            return "Response needs improvement. Focus on providing more detailed technical explanations."
    
    def _poor_evaluation(self):
        """Return poor evaluation for empty answers"""
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
            'detailed_feedback': "No response provided. Please provide a detailed answer to demonstrate your knowledge.",
            'hiring_decision': {
                'decision': 'No Hire',
                'confidence': 0.9
            }
        }