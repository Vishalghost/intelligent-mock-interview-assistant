import boto3
import json
from typing import List, Dict

class QuestionGenerator:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    def generate_questions(self, candidate_data: Dict, role: str) -> List[str]:
        prompt = f"""
        Generate 5 interview questions for a {role} position.
        Candidate skills: {', '.join(candidate_data['skills'])}
        Experience: {candidate_data['experience_years']} years
        
        Focus on technical skills and behavioral questions.
        Return only the questions, one per line.
        """
        
        try:
            response = self.bedrock.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 1000,
                    'messages': [{'role': 'user', 'content': prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            questions = result['content'][0]['text'].strip().split('\n')
            return [q.strip() for q in questions if q.strip()]
            
        except Exception as e:
            # Fallback questions
            return [
                f"Describe your experience with {candidate_data['skills'][0] if candidate_data['skills'] else 'programming'}",
                "Tell me about a challenging project you worked on",
                "How do you handle tight deadlines?",
                "What motivates you in your work?",
                "Where do you see yourself in 5 years?"
            ]