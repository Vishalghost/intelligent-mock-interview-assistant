import boto3
import json
from typing import Dict, List

class ResourcesGenerator:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    def generate_personalized_resources(self, evaluation_results: Dict, candidate_profile: Dict, role: str) -> Dict:
        """Generate personalized learning resources based on performance"""
        
        faang_score = evaluation_results.get('faang_score', 0)
        weak_areas = self._identify_weak_areas(evaluation_results)
        strong_areas = self._identify_strong_areas(evaluation_results)
        
        resources = {
            'immediate_action_plan': self._generate_action_plan(faang_score, weak_areas, role),
            'technical_resources': self._generate_technical_resources(weak_areas, candidate_profile),
            'system_design_resources': self._generate_system_design_resources(faang_score),
            'algorithmic_resources': self._generate_algorithmic_resources(faang_score),
            'behavioral_resources': self._generate_behavioral_resources(weak_areas),
            'faang_specific_prep': self._generate_faang_prep(role, faang_score),
            'practice_platforms': self._get_practice_platforms(),
            'books_and_courses': self._get_recommended_books(weak_areas, role),
            'mock_interview_plan': self._generate_mock_interview_plan(faang_score),
            'timeline_roadmap': self._generate_timeline_roadmap(faang_score, weak_areas)
        }
        
        return resources
    
    def _identify_weak_areas(self, evaluation_results: Dict) -> List[str]:
        """Identify areas needing improvement"""
        weak_areas = []
        dimension_scores = evaluation_results.get('dimension_scores', {})
        
        for dimension, score in dimension_scores.items():
            if score < 70:
                weak_areas.append(dimension)
        
        return weak_areas
    
    def _identify_strong_areas(self, evaluation_results: Dict) -> List[str]:
        """Identify strong areas to leverage"""
        strong_areas = []
        dimension_scores = evaluation_results.get('dimension_scores', {})
        
        for dimension, score in dimension_scores.items():
            if score >= 80:
                strong_areas.append(dimension)
        
        return strong_areas
    
    def _generate_action_plan(self, faang_score: float, weak_areas: List[str], role: str) -> List[Dict]:
        """Generate immediate action plan"""
        
        if faang_score >= 85:
            return [
                {
                    'priority': 'HIGH',
                    'action': 'Apply to FAANG companies immediately',
                    'timeline': '1-2 weeks',
                    'details': 'You are ready for senior-level FAANG interviews'
                },
                {
                    'priority': 'MEDIUM',
                    'action': 'Practice company-specific questions',
                    'timeline': '2-3 weeks',
                    'details': 'Focus on Google, Amazon, Meta specific interview styles'
                }
            ]
        elif faang_score >= 70:
            return [
                {
                    'priority': 'HIGH',
                    'action': 'Intensive 4-week FAANG prep bootcamp',
                    'timeline': '4 weeks',
                    'details': 'Focus on system design and advanced algorithms'
                },
                {
                    'priority': 'HIGH',
                    'action': 'Daily mock interviews with FAANG engineers',
                    'timeline': '4 weeks',
                    'details': 'Practice with Pramp, Interviewing.io, or similar platforms'
                }
            ]
        else:
            return [
                {
                    'priority': 'CRITICAL',
                    'action': 'Fundamental skill building program',
                    'timeline': '3-6 months',
                    'details': 'Build strong foundation before attempting FAANG interviews'
                },
                {
                    'priority': 'HIGH',
                    'action': 'Complete structured learning path',
                    'timeline': '6 months',
                    'details': 'Follow systematic curriculum for technical depth'
                }
            ]
    
    def _generate_technical_resources(self, weak_areas: List[str], candidate_profile: Dict) -> Dict:
        """Generate technical learning resources"""
        
        resources = {
            'technical_mastery': {
                'courses': [
                    'MIT 6.006 Introduction to Algorithms (OpenCourseWare)',
                    'Stanford CS161 Design and Analysis of Algorithms',
                    'Coursera - Algorithms Specialization by Stanford'
                ],
                'books': [
                    'Introduction to Algorithms (CLRS)',
                    'Algorithm Design Manual by Steven Skiena',
                    'Programming Pearls by Jon Bentley'
                ],
                'practice': [
                    'LeetCode Premium (focus on Hard problems)',
                    'HackerRank Algorithm challenges',
                    'CodeSignal Company Challenges'
                ]
            },
            'system_thinking': {
                'courses': [
                    'MIT 6.824 Distributed Systems',
                    'CMU 15-440 Distributed Systems',
                    'Grokking the System Design Interview'
                ],
                'books': [
                    'Designing Data-Intensive Applications by Martin Kleppmann',
                    'System Design Interview by Alex Xu',
                    'Building Microservices by Sam Newman'
                ],
                'practice': [
                    'System Design Primer (GitHub)',
                    'High Scalability blog case studies',
                    'AWS Architecture Center'
                ]
            },
            'communication_excellence': {
                'courses': [
                    'Technical Communication for Engineers',
                    'Presentation Skills for Technical Professionals',
                    'Executive Communication Coaching'
                ],
                'practice': [
                    'Toastmasters International',
                    'Record and review technical explanations',
                    'Teach concepts to non-technical people'
                ]
            }
        }
        
        return resources
    
    def _generate_system_design_resources(self, faang_score: float) -> Dict:
        """Generate system design specific resources"""
        
        if faang_score >= 80:
            level = 'advanced'
        elif faang_score >= 60:
            level = 'intermediate'
        else:
            level = 'beginner'
        
        resources = {
            'beginner': {
                'start_here': [
                    'System Design Primer (GitHub) - Complete walkthrough',
                    'Grokking the System Design Interview - Educative.io',
                    'System Design Interview questions - InterviewBit'
                ],
                'key_concepts': [
                    'Load Balancing', 'Caching', 'Database Sharding',
                    'Microservices', 'Message Queues', 'CDN'
                ],
                'practice_problems': [
                    'Design a URL shortener (like bit.ly)',
                    'Design a chat system (like WhatsApp)',
                    'Design a news feed (like Facebook)'
                ]
            },
            'intermediate': {
                'advanced_topics': [
                    'Distributed Consensus (Raft, Paxos)',
                    'Event Sourcing and CQRS',
                    'Microservices Patterns',
                    'Distributed Caching Strategies'
                ],
                'practice_problems': [
                    'Design Netflix video streaming',
                    'Design Uber ride-sharing system',
                    'Design distributed search engine'
                ]
            },
            'advanced': {
                'expert_topics': [
                    'Distributed Systems Theory',
                    'Consensus Algorithms Implementation',
                    'Large-scale Data Processing',
                    'Global Distribution Strategies'
                ],
                'practice_problems': [
                    'Design global CDN like CloudFlare',
                    'Design distributed database like Spanner',
                    'Design real-time analytics like Google Analytics'
                ]
            }
        }
        
        return resources[level]
    
    def _generate_algorithmic_resources(self, faang_score: float) -> Dict:
        """Generate algorithm-specific resources"""
        
        return {
            'platforms': {
                'LeetCode': {
                    'focus': 'FAANG-style problems',
                    'recommendation': 'Premium subscription for company-specific questions',
                    'daily_target': '2-3 problems (focus on Hard difficulty)'
                },
                'HackerRank': {
                    'focus': 'Algorithm fundamentals',
                    'recommendation': 'Complete all algorithm tracks',
                    'daily_target': '1-2 problems'
                },
                'CodeSignal': {
                    'focus': 'Company assessments',
                    'recommendation': 'Practice company-specific challenges',
                    'daily_target': '1 company challenge'
                }
            },
            'study_plan': {
                'week_1_2': ['Arrays and Strings', 'Linked Lists', 'Stacks and Queues'],
                'week_3_4': ['Trees and Graphs', 'Dynamic Programming Basics'],
                'week_5_6': ['Advanced DP', 'Backtracking', 'Greedy Algorithms'],
                'week_7_8': ['Advanced Graph Algorithms', 'String Algorithms'],
                'week_9_12': ['System Design + Advanced Algorithms Integration']
            },
            'difficulty_progression': {
                'month_1': '70% Easy, 30% Medium',
                'month_2': '30% Easy, 60% Medium, 10% Hard',
                'month_3': '10% Easy, 40% Medium, 50% Hard',
                'month_4+': '0% Easy, 30% Medium, 70% Hard'
            }
        }
    
    def _generate_behavioral_resources(self, weak_areas: List[str]) -> Dict:
        """Generate behavioral interview resources"""
        
        return {
            'frameworks': {
                'STAR_method': {
                    'description': 'Situation, Task, Action, Result framework',
                    'practice': 'Prepare 20+ STAR stories covering different scenarios',
                    'resources': ['Amazon Leadership Principles examples', 'Google behavioral guide']
                },
                'leadership_principles': {
                    'amazon': ['Customer Obsession', 'Ownership', 'Invent and Simplify', 'Learn and Be Curious'],
                    'google': ['Googleyness', 'Leadership', 'Role-related knowledge', 'General cognitive ability'],
                    'meta': ['Move Fast', 'Be Bold', 'Focus on Impact', 'Be Open']
                }
            },
            'story_categories': [
                'Leadership and influence',
                'Dealing with conflict',
                'Failure and learning',
                'Innovation and creativity',
                'Working under pressure',
                'Cross-functional collaboration'
            ],
            'preparation_steps': [
                '1. Identify 20+ professional experiences',
                '2. Map experiences to leadership principles',
                '3. Structure using STAR method',
                '4. Practice with mock interviews',
                '5. Record and review responses'
            ]
        }
    
    def _generate_faang_prep(self, role: str, faang_score: float) -> Dict:
        """Generate FAANG-specific preparation resources"""
        
        return {
            'company_specific': {
                'Google': {
                    'focus_areas': ['System Design', 'Algorithms', 'Googleyness'],
                    'resources': ['Google Engineering Blog', 'Google Research Papers'],
                    'interview_style': 'Technical depth with collaborative problem-solving'
                },
                'Amazon': {
                    'focus_areas': ['Leadership Principles', 'System Design', 'Customer Obsession'],
                    'resources': ['Amazon Leadership Principles Guide', 'AWS Architecture'],
                    'interview_style': 'Behavioral heavy with technical depth'
                },
                'Meta': {
                    'focus_areas': ['System Design at Scale', 'Product Sense', 'Culture Fit'],
                    'resources': ['Meta Engineering Blog', 'React/GraphQL deep dives'],
                    'interview_style': 'Fast-paced with focus on impact'
                },
                'Apple': {
                    'focus_areas': ['Product Excellence', 'Technical Innovation', 'Attention to Detail'],
                    'resources': ['Apple Developer Documentation', 'WWDC Sessions'],
                    'interview_style': 'Deep technical with product focus'
                },
                'Netflix': {
                    'focus_areas': ['High Performance Culture', 'Innovation', 'Scale Challenges'],
                    'resources': ['Netflix Tech Blog', 'Microservices Architecture'],
                    'interview_style': 'Culture fit with technical excellence'
                }
            },
            'insider_tips': [
                'Study the company\'s engineering blog religiously',
                'Understand their specific technical challenges and solutions',
                'Practice explaining complex concepts simply',
                'Prepare questions that show genuine interest in their problems',
                'Research recent product launches and technical decisions'
            ]
        }
    
    def _get_practice_platforms(self) -> Dict:
        """Get recommended practice platforms"""
        
        return {
            'mock_interviews': {
                'Pramp': 'Free peer-to-peer mock interviews',
                'Interviewing.io': 'Anonymous interviews with engineers',
                'InterviewBuddy': 'Professional mock interview service',
                'Gainlo': 'Mock interviews with ex-FAANG engineers'
            },
            'coding_practice': {
                'LeetCode': 'Primary platform for algorithm practice',
                'HackerRank': 'Comprehensive skill assessment',
                'CodeSignal': 'Company-specific challenges',
                'AlgoExpert': 'Curated problems with video explanations'
            },
            'system_design': {
                'Educative.io': 'Grokking the System Design Interview',
                'InterviewReady': 'System design course with practice',
                'SystemsExpert': 'AlgoExpert\'s system design course'
            }
        }
    
    def _get_recommended_books(self, weak_areas: List[str], role: str) -> List[Dict]:
        """Get recommended books based on weak areas"""
        
        books = [
            {
                'title': 'Cracking the Coding Interview',
                'author': 'Gayle Laakmann McDowell',
                'focus': 'General interview preparation',
                'priority': 'HIGH',
                'estimated_time': '4-6 weeks'
            },
            {
                'title': 'System Design Interview',
                'author': 'Alex Xu',
                'focus': 'System design fundamentals',
                'priority': 'HIGH',
                'estimated_time': '3-4 weeks'
            },
            {
                'title': 'Designing Data-Intensive Applications',
                'author': 'Martin Kleppmann',
                'focus': 'Advanced system design',
                'priority': 'MEDIUM',
                'estimated_time': '8-10 weeks'
            },
            {
                'title': 'Introduction to Algorithms (CLRS)',
                'author': 'Cormen, Leiserson, Rivest, Stein',
                'focus': 'Algorithm fundamentals',
                'priority': 'MEDIUM',
                'estimated_time': '12+ weeks'
            }
        ]
        
        return books
    
    def _generate_mock_interview_plan(self, faang_score: float) -> Dict:
        """Generate mock interview schedule"""
        
        if faang_score >= 80:
            frequency = 'Daily'
            duration = '2-3 weeks'
            focus = 'Company-specific practice'
        elif faang_score >= 60:
            frequency = '3-4 times per week'
            duration = '4-6 weeks'
            focus = 'Mixed technical and behavioral'
        else:
            frequency = '2-3 times per week'
            duration = '8-12 weeks'
            focus = 'Fundamental skill building'
        
        return {
            'frequency': frequency,
            'duration': duration,
            'focus': focus,
            'schedule': {
                'week_1': 'Algorithm practice + basic behavioral',
                'week_2': 'System design + advanced behavioral',
                'week_3': 'Mixed practice + company-specific',
                'week_4+': 'Full interview simulations'
            }
        }
    
    def _generate_timeline_roadmap(self, faang_score: float, weak_areas: List[str]) -> Dict:
        """Generate personalized timeline roadmap"""
        
        if faang_score >= 85:
            timeline = '2-4 weeks'
            readiness = 'Interview Ready'
        elif faang_score >= 70:
            timeline = '6-8 weeks'
            readiness = 'Near Ready'
        elif faang_score >= 50:
            timeline = '3-6 months'
            readiness = 'Preparation Needed'
        else:
            timeline = '6-12 months'
            readiness = 'Foundation Building Required'
        
        return {
            'estimated_timeline': timeline,
            'current_readiness': readiness,
            'milestones': {
                'month_1': 'Complete fundamental gaps',
                'month_2': 'Advanced problem solving',
                'month_3': 'System design mastery',
                'month_4': 'Mock interview excellence',
                'month_5': 'Company-specific preparation',
                'month_6': 'Interview execution'
            },
            'success_metrics': [
                'Solve 80% of LeetCode Hard problems',
                'Design systems for 1B+ users confidently',
                'Score 90%+ in mock interviews',
                'Demonstrate clear leadership examples',
                'Explain complex concepts simply'
            ]
        }