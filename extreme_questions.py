import boto3
import json
import random
import hashlib
from typing import Dict, List

class ExtremeQuestions:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.used_questions = set()
        
    def generate_extreme_questions(self, candidate_data: Dict, role: str) -> List[Dict]:
        """Generate extremely difficult, out-of-the-box questions"""
        
        questions = []
        
        # Generate 8 unique extreme questions
        for i in range(8):
            question = self._generate_extreme_question(candidate_data, role, i)
            if self._is_unique(question):
                questions.append(question)
                self._mark_used(question)
        
        return questions
    
    def _generate_extreme_question(self, candidate_data: Dict, role: str, index: int) -> Dict:
        """Generate single extreme question with AI"""
        
        prompt = f"""
        Generate an EXTREMELY DIFFICULT, OUT-OF-THE-BOX interview question for {role} at top-tier tech company level.
        
        Requirements:
        - Must be INSANELY DIFFICULT - beyond typical interview questions
        - Requires CREATIVE, UNCONVENTIONAL thinking
        - No standard textbook solutions exist
        - Forces candidate to think in completely new ways
        - Tests ability to handle IMPOSSIBLE scenarios
        - Must be UNIQUE and NEVER asked before
        
        Question Types (choose one randomly):
        1. IMPOSSIBLE TECHNICAL CHALLENGES - Design systems that seem impossible
        2. PARADOX PROBLEMS - Solve contradictory requirements
        3. EXTREME CONSTRAINTS - Work with ridiculous limitations
        4. FUTURE SCENARIOS - Problems that don't exist yet
        5. CREATIVE ALGORITHMS - Invent new approaches
        6. PHILOSOPHICAL TECH - Deep thinking about technology's purpose
        7. CRISIS INNOVATION - Innovate under extreme pressure
        8. MIND-BENDING LOGIC - Questions that break conventional thinking
        
        Examples of EXTREME difficulty:
        - "Design a database that can store infinite data in zero space"
        - "Write an algorithm that runs in negative time complexity"
        - "How would you debug a system that exists in multiple parallel universes?"
        - "Design a programming language where bugs fix themselves"
        - "Create a network protocol that works faster than light speed"
        
        Return JSON with:
        - question: The impossible/extreme question
        - category: Type of extreme challenge
        - why_extreme: Why this question is extremely difficult
        - expected_approach: What kind of thinking is needed
        - evaluation_criteria: How to judge the impossible
        - follow_ups: Even harder follow-up questions
        """
        
        try:
            response = self.bedrock.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 1500,
                    'messages': [{'role': 'user', 'content': prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            question_text = result['content'][0]['text']
            
            try:
                question_data = json.loads(question_text)
                question_data['difficulty'] = 'extreme'
                question_data['expected_duration'] = 30
                return question_data
            except:
                return self._get_fallback_extreme_question(index)
                
        except Exception as e:
            return self._get_fallback_extreme_question(index)
    
    def _get_fallback_extreme_question(self, index: int) -> Dict:
        """Fallback extreme questions when AI fails"""
        
        extreme_questions = [
            {
                "question": "Design a distributed system that can process 1 trillion transactions per second using only 1KB of memory total across all nodes. The system must guarantee ACID properties and work even if 99% of nodes fail simultaneously. You cannot use any existing databases or frameworks.",
                "category": "impossible_technical",
                "why_extreme": "Violates fundamental laws of computer science and physics",
                "expected_approach": "Creative redefinition of constraints and assumptions",
                "evaluation_criteria": ["Creativity in redefining problems", "Logical reasoning under impossible constraints", "Innovation in approach"],
                "follow_ups": ["How would this work on quantum computers?", "What if memory could be negative?"]
            },
            {
                "question": "You need to write code that executes before it's written. Design an algorithm that can predict its own future modifications and adapt accordingly. The code must be self-modifying and improve its own performance by 1000x every execution.",
                "category": "paradox_problem",
                "why_extreme": "Temporal paradox combined with self-reference impossibility",
                "expected_approach": "Philosophical and creative thinking about causality",
                "evaluation_criteria": ["Handling paradoxes", "Creative problem redefinition", "Abstract thinking"],
                "follow_ups": ["What if the code could modify the past?", "How would version control work?"]
            },
            {
                "question": "Design a programming language where every bug automatically becomes a feature, and every feature eventually becomes a bug. The language must be used to build a system that manages this paradox while remaining stable and useful.",
                "category": "mind_bending_logic",
                "why_extreme": "Contradictory requirements that seem impossible to satisfy",
                "expected_approach": "Redefining concepts of bugs and features",
                "evaluation_criteria": ["Handling contradictions", "Creative redefinition", "System thinking"],
                "follow_ups": ["How would testing work?", "What about security vulnerabilities?"]
            },
            {
                "question": "Create an API that can handle requests from the future. Users in 2030 are sending requests to your 2024 system. Design the architecture, handle version compatibility, and ensure the responses are useful 6 years before the questions are asked.",
                "category": "future_scenario",
                "why_extreme": "Time travel and prediction of unknown future requirements",
                "expected_approach": "Extreme forward thinking and adaptability design",
                "evaluation_criteria": ["Future-proofing strategies", "Adaptability design", "Creative time handling"],
                "follow_ups": ["What if multiple timelines exist?", "How to handle paradoxes?"]
            },
            {
                "question": "Design a search algorithm that finds things that don't exist yet. It should return results for queries about concepts, technologies, or solutions that haven't been invented. The algorithm must be 99.9% accurate about future inventions.",
                "category": "creative_algorithms",
                "why_extreme": "Searching for non-existent information with high accuracy",
                "expected_approach": "Predictive modeling and creative extrapolation",
                "evaluation_criteria": ["Predictive thinking", "Creative extrapolation", "Logical reasoning"],
                "follow_ups": ["How to validate accuracy?", "What about ethical implications?"]
            },
            {
                "question": "You're tasked with debugging a system that exists simultaneously in multiple parallel universes. Each universe has different laws of physics and computing. A bug in one universe affects all others. How do you debug across infinite realities?",
                "category": "crisis_innovation",
                "why_extreme": "Multi-dimensional debugging with infinite complexity",
                "expected_approach": "Abstract thinking about parallel systems",
                "evaluation_criteria": ["Multi-dimensional thinking", "Abstract problem solving", "Creative debugging"],
                "follow_ups": ["What if universes merge?", "How to deploy fixes across realities?"]
            },
            {
                "question": "Design a data structure that can store more information than physically possible. It should compress infinite data into finite space while maintaining O(1) access time and perfect data integrity. Explain how this violates and transcends computational limits.",
                "category": "impossible_technical",
                "why_extreme": "Violates fundamental information theory and physics",
                "expected_approach": "Creative redefinition of information and storage",
                "evaluation_criteria": ["Creative constraint handling", "Information theory understanding", "Innovation"],
                "follow_ups": ["How would garbage collection work?", "What about quantum effects?"]
            },
            {
                "question": "Create a machine learning model that can learn concepts that humans haven't discovered yet. The model should teach humans new mathematical theorems, scientific principles, and technological possibilities. How do you validate knowledge that doesn't exist in human understanding?",
                "category": "philosophical_tech",
                "why_extreme": "Learning beyond human knowledge with validation challenges",
                "expected_approach": "Philosophical thinking about knowledge and discovery",
                "evaluation_criteria": ["Philosophical depth", "Creative validation methods", "Abstract reasoning"],
                "follow_ups": ["How to communicate undiscovered concepts?", "What about safety of unknown knowledge?"]
            }
        ]
        
        question = extreme_questions[index % len(extreme_questions)]
        question['difficulty'] = 'extreme'
        question['expected_duration'] = 30
        return question
    
    def generate_system_breaking_questions(self, candidate_data: Dict, role: str) -> List[Dict]:
        """Generate questions that break conventional system thinking"""
        
        skills = candidate_data.get('skills', [])
        breaking_questions = []
        
        for skill in skills[:3]:
            prompt = f"""
            Generate a SYSTEM-BREAKING question about {skill} that challenges fundamental assumptions.
            
            Requirements:
            - Must challenge basic assumptions about {skill}
            - Force candidate to think beyond conventional limits
            - No standard solutions should exist
            - Should break normal thinking patterns
            - Extremely difficult even for experts
            
            Examples:
            - "How would you use {skill} if computers could only subtract?"
            - "Design {skill} architecture for beings that think in 11 dimensions"
            - "Implement {skill} where every operation must be reversible"
            
            Return JSON with:
            - question: The system-breaking challenge
            - broken_assumption: What assumption this breaks
            - conventional_approach: Why normal methods fail
            - required_thinking: Type of thinking needed
            - evaluation_criteria: How to judge responses
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
                question_text = result['content'][0]['text']
                
                try:
                    question_data = json.loads(question_text)
                    question_data['category'] = 'system_breaking'
                    question_data['technology'] = skill
                    question_data['difficulty'] = 'extreme'
                    breaking_questions.append(question_data)
                except:
                    # Fallback system-breaking question
                    breaking_questions.append({
                        'question': f'Design a {skill} system that works in reverse - where outputs determine inputs and effects precede causes. The system must be practical and solve real problems.',
                        'category': 'system_breaking',
                        'technology': skill,
                        'broken_assumption': 'Causality and normal flow direction',
                        'difficulty': 'extreme',
                        'evaluation_criteria': ['Reverse thinking', 'Causality handling', 'Practical application']
                    })
            except:
                continue
        
        return breaking_questions
    
    def generate_paradox_questions(self, candidate_data: Dict, role: str) -> List[Dict]:
        """Generate paradox-based questions that seem impossible"""
        
        paradox_prompts = [
            "Create a security system that is completely open yet perfectly secure",
            "Design a database that forgets everything but remembers perfectly",
            "Build a network that is infinitely fast yet uses no bandwidth",
            "Develop software that is bug-free but constantly changing",
            "Create an algorithm that is both deterministic and random"
        ]
        
        paradox_questions = []
        
        for prompt_base in paradox_prompts:
            prompt = f"""
            Expand this paradox into an EXTREME interview question: "{prompt_base}"
            
            Requirements:
            - Make it seem genuinely impossible
            - Force creative redefinition of concepts
            - No obvious solutions should exist
            - Test ability to handle contradictions
            - Push beyond normal logical thinking
            
            Return JSON with:
            - question: The expanded paradox question
            - paradox_type: What makes this paradoxical
            - resolution_approach: How one might approach this
            - evaluation_criteria: What to look for in answers
            - mind_bender_factor: Why this breaks normal thinking
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
                question_text = result['content'][0]['text']
                
                try:
                    question_data = json.loads(question_text)
                    question_data['category'] = 'paradox_challenge'
                    question_data['difficulty'] = 'extreme'
                    paradox_questions.append(question_data)
                except:
                    continue
            except:
                continue
        
        return paradox_questions[:3]  # Return top 3 paradox questions
    
    def _is_unique(self, question: Dict) -> bool:
        """Check if question is unique"""
        question_text = question.get('question', '')
        question_hash = hashlib.md5(question_text.encode()).hexdigest()
        return question_hash not in self.used_questions
    
    def _mark_used(self, question: Dict):
        """Mark question as used"""
        question_text = question.get('question', '')
        question_hash = hashlib.md5(question_text.encode()).hexdigest()
        self.used_questions.add(question_hash)