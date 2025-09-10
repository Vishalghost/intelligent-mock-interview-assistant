import boto3
import json
import numpy as np
from typing import Dict, List, Tuple
import re
from datetime import datetime

class AdvancedEvaluator:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.comprehend = boto3.client('comprehend', region_name='us-east-1')
        
    def evaluate_response(self, question_data: Dict, answer: str, role: str, candidate_profile: Dict) -> Dict:
        """Evaluate responses against top-tier tech company standards with extreme rigor"""
        
        # Advanced evaluation dimensions with higher standards
        technical_mastery = self._evaluate_technical_mastery(answer, question_data, candidate_profile)
        problem_solving_depth = self._evaluate_problem_solving_depth(answer, question_data)
        communication_excellence = self._evaluate_communication_excellence(answer)
        innovation_thinking = self._evaluate_innovation_thinking(answer, question_data)
        leadership_potential = self._evaluate_leadership_potential(answer, question_data)
        system_thinking = self._evaluate_system_thinking(answer, question_data)
        
        # AI-powered deep analysis
        ai_analysis = self._ai_deep_analysis(question_data, answer, role)
        
        # Calculate weighted score (much stricter)
        weights = {
            'technical_mastery': 0.25,
            'problem_solving_depth': 0.20,
            'communication_excellence': 0.15,
            'innovation_thinking': 0.15,
            'leadership_potential': 0.15,
            'system_thinking': 0.10
        }
        
        weighted_score = (
            technical_mastery * weights['technical_mastery'] +
            problem_solving_depth * weights['problem_solving_depth'] +
            communication_excellence * weights['communication_excellence'] +
            innovation_thinking * weights['innovation_thinking'] +
            leadership_potential * weights['leadership_potential'] +
            system_thinking * weights['system_thinking']
        )
        
        # Hiring decision
        hiring_decision = self._make_hiring_decision(weighted_score, ai_analysis)
        
        # Generate comprehensive feedback
        detailed_feedback = self._generate_detailed_feedback(
            technical_mastery, problem_solving_depth, communication_excellence,
            innovation_thinking, leadership_potential, system_thinking, ai_analysis
        )
        
        return {
            'overall_score': round(weighted_score, 1),
            'hiring_decision': hiring_decision,
            'dimension_scores': {
                'technical_mastery': technical_mastery,
                'problem_solving_depth': problem_solving_depth,
                'communication_excellence': communication_excellence,
                'innovation_thinking': innovation_thinking,
                'leadership_potential': leadership_potential,
                'system_thinking': system_thinking
            },
            'ai_analysis': ai_analysis,
            'detailed_feedback': detailed_feedback,
            'improvement_roadmap': self._generate_improvement_roadmap(weighted_score, ai_analysis),
            'readiness_level': self._assess_readiness(weighted_score, ai_analysis),
            'next_interview_prep': self._generate_prep_recommendations(weighted_score, question_data['category'])
        }
    
    def _evaluate_technical_mastery(self, answer: str, question_data: Dict, candidate_profile: Dict) -> float:
        """Evaluate technical depth against top-tier standards (extremely rigorous)"""
        score = 0
        answer_lower = answer.lower()
        
        # Advanced technical concepts
        advanced_concepts = [
            'distributed systems', 'microservices', 'event sourcing', 'cqrs',
            'eventual consistency', 'cap theorem', 'acid properties', 'base properties',
            'consensus algorithms', 'raft', 'paxos', 'byzantine fault tolerance',
            'load balancing', 'circuit breaker', 'bulkhead pattern', 'saga pattern',
            'caching strategies', 'cache coherence', 'memory hierarchy', 'cpu cache',
            'garbage collection', 'memory management', 'jvm internals', 'compiler optimization',
            'concurrency', 'parallelism', 'lock-free programming', 'atomic operations',
            'database internals', 'b-tree', 'lsm tree', 'mvcc', 'isolation levels',
            'networking', 'tcp/ip', 'http/2', 'websockets', 'grpc', 'message queues'
        ]
        
        concept_mentions = sum(1 for concept in advanced_concepts if concept in answer_lower)
        score += min(30, concept_mentions * 2)
        
        # System design principles
        design_principles = [
            'scalability', 'reliability', 'availability', 'consistency', 'partition tolerance',
            'fault tolerance', 'disaster recovery', 'monitoring', 'observability',
            'security', 'authentication', 'authorization', 'encryption', 'data privacy'
        ]
        
        principle_mentions = sum(1 for principle in design_principles if principle in answer_lower)
        score += min(25, principle_mentions * 2)
        
        # Specific technology depth
        candidate_skills = candidate_profile.get('skills', [])
        for skill in candidate_skills:
            if skill in answer_lower:
                if any(detail in answer_lower for detail in ['internal', 'architecture', 'implementation', 'optimization']):
                    score += 5
        
        # Code quality indicators
        code_quality = ['clean code', 'solid principles', 'design patterns', 'refactoring', 'testing']
        quality_mentions = sum(1 for quality in code_quality if quality in answer_lower)
        score += min(15, quality_mentions * 3)
        
        # Performance considerations
        performance_terms = ['performance', 'optimization', 'latency', 'throughput', 'bottleneck', 'profiling']
        perf_mentions = sum(1 for term in performance_terms if term in answer_lower)
        score += min(20, perf_mentions * 4)
        
        # Deduct points for shallow answers
        word_count = len(answer.split())
        if word_count < 100:
            score *= 0.5
        elif word_count < 200:
            score *= 0.7
        
        return min(100, score)
    
    def _evaluate_problem_solving_depth(self, answer: str, question_data: Dict) -> float:
        """Evaluate problem-solving approach with extreme rigor"""
        score = 0
        answer_lower = answer.lower()
        
        # Structured thinking
        structure_indicators = [
            'first', 'second', 'third', 'step 1', 'step 2', 'initially', 'then', 'next', 'finally',
            'approach', 'strategy', 'methodology', 'framework', 'process'
        ]
        structure_count = sum(1 for indicator in structure_indicators if indicator in answer_lower)
        score += min(25, structure_count * 3)
        
        # Problem decomposition
        decomposition_words = [
            'break down', 'decompose', 'divide', 'separate', 'isolate', 'component',
            'module', 'layer', 'abstraction', 'interface'
        ]
        decomp_count = sum(1 for word in decomposition_words if word in answer_lower)
        score += min(20, decomp_count * 4)
        
        # Trade-off analysis
        tradeoff_indicators = [
            'trade-off', 'tradeoff', 'pros and cons', 'advantages', 'disadvantages',
            'benefit', 'cost', 'compromise', 'balance', 'versus', 'vs', 'compared to'
        ]
        tradeoff_count = sum(1 for indicator in tradeoff_indicators if indicator in answer_lower)
        score += min(25, tradeoff_count * 5)
        
        # Edge case consideration
        edge_case_words = [
            'edge case', 'corner case', 'boundary', 'limit', 'exception', 'error handling',
            'failure', 'fallback', 'contingency', 'what if', 'edge condition'
        ]
        edge_count = sum(1 for word in edge_case_words if word in answer_lower)
        score += min(20, edge_count * 4)
        
        # Scalability thinking
        scale_words = [
            'scale', 'scaling', 'growth', 'volume', 'load', 'capacity', 'throughput',
            'million', 'billion', 'users', 'requests', 'data size'
        ]
        scale_count = sum(1 for word in scale_words if word in answer_lower)
        score += min(10, scale_count * 2)
        
        return min(100, score)
    
    def _evaluate_communication_excellence(self, answer: str) -> float:
        """Evaluate communication against top-tier standards"""
        score = 0
        
        # Clarity and structure
        sentences = [s.strip() for s in answer.split('.') if s.strip()]
        if len(sentences) >= 5:
            score += 20
        
        # Professional vocabulary
        professional_terms = [
            'implement', 'develop', 'architect', 'design', 'optimize', 'analyze',
            'evaluate', 'assess', 'collaborate', 'coordinate', 'facilitate', 'deliver'
        ]
        prof_count = sum(1 for term in professional_terms if term in answer.lower())
        score += min(20, prof_count * 3)
        
        # Technical communication
        explanation_words = [
            'because', 'therefore', 'however', 'moreover', 'furthermore', 'consequently',
            'as a result', 'in addition', 'for example', 'specifically', 'in particular'
        ]
        explanation_count = sum(1 for word in explanation_words if word in answer.lower())
        score += min(25, explanation_count * 4)
        
        # Confidence indicators
        confidence_words = [
            'confident', 'experienced', 'successfully', 'achieved', 'delivered',
            'proven', 'demonstrated', 'expertise', 'proficient', 'skilled'
        ]
        conf_count = sum(1 for word in confidence_words if word in answer.lower())
        score += min(15, conf_count * 3)
        
        # Answer completeness
        word_count = len(answer.split())
        if 200 <= word_count <= 500:
            score += 20
        elif word_count > 500:
            score += 10
        elif word_count < 100:
            score -= 20
        
        return max(0, min(100, score))
    
    def _evaluate_innovation_thinking(self, answer: str, question_data: Dict) -> float:
        """Evaluate innovative and creative thinking"""
        score = 0
        answer_lower = answer.lower()
        
        # Innovation indicators
        innovation_words = [
            'innovative', 'creative', 'novel', 'unique', 'original', 'breakthrough',
            'disruptive', 'revolutionary', 'cutting-edge', 'state-of-the-art',
            'reimagine', 'rethink', 'reinvent', 'transform', 'paradigm'
        ]
        innovation_count = sum(1 for word in innovation_words if word in answer_lower)
        score += min(25, innovation_count * 5)
        
        # Alternative approaches
        alternative_words = [
            'alternative', 'different approach', 'another way', 'alternatively',
            'option', 'variation', 'modification', 'adaptation', 'customization'
        ]
        alt_count = sum(1 for word in alternative_words if word in answer_lower)
        score += min(20, alt_count * 4)
        
        # Future thinking
        future_words = [
            'future', 'evolve', 'adapt', 'scale', 'extend', 'enhance', 'improve',
            'next generation', 'roadmap', 'vision', 'long-term', 'strategic'
        ]
        future_count = sum(1 for word in future_words if word in answer_lower)
        score += min(20, future_count * 4)
        
        # Creative problem solving
        creative_words = [
            'creative', 'outside the box', 'unconventional', 'non-traditional',
            'experimental', 'prototype', 'proof of concept', 'pilot', 'trial'
        ]
        creative_count = sum(1 for word in creative_words if word in answer_lower)
        score += min(25, creative_count * 5)
        
        # Technology trends awareness
        trend_words = [
            'ai', 'machine learning', 'blockchain', 'cloud native', 'serverless',
            'microservices', 'containerization', 'devops', 'automation', 'iot'
        ]
        trend_count = sum(1 for word in trend_words if word in answer_lower)
        score += min(10, trend_count * 2)
        
        return min(100, score)
    
    def _evaluate_leadership_potential(self, answer: str, question_data: Dict) -> float:
        """Evaluate leadership qualities"""
        score = 0
        answer_lower = answer.lower()
        
        # Leadership actions
        leadership_actions = [
            'led', 'managed', 'coordinated', 'organized', 'facilitated', 'guided',
            'mentored', 'coached', 'influenced', 'motivated', 'inspired', 'empowered'
        ]
        leadership_count = sum(1 for action in leadership_actions if action in answer_lower)
        score += min(30, leadership_count * 5)
        
        # Decision making
        decision_words = [
            'decided', 'chose', 'selected', 'determined', 'concluded', 'resolved',
            'judgment', 'decision', 'choice', 'option', 'recommendation'
        ]
        decision_count = sum(1 for word in decision_words if word in answer_lower)
        score += min(25, decision_count * 5)
        
        # Team collaboration
        team_words = [
            'team', 'collaborate', 'cooperation', 'partnership', 'stakeholder',
            'cross-functional', 'interdisciplinary', 'coordination', 'alignment'
        ]
        team_count = sum(1 for word in team_words if word in answer_lower)
        score += min(20, team_count * 4)
        
        # Ownership and accountability
        ownership_words = [
            'ownership', 'responsible', 'accountable', 'committed', 'dedicated',
            'initiative', 'proactive', 'drive', 'champion', 'advocate'
        ]
        ownership_count = sum(1 for word in ownership_words if word in answer_lower)
        score += min(25, ownership_count * 5)
        
        return min(100, score)
    
    def _evaluate_system_thinking(self, answer: str, question_data: Dict) -> float:
        """Evaluate systems thinking and holistic approach"""
        score = 0
        answer_lower = answer.lower()
        
        # Systems concepts
        system_words = [
            'system', 'architecture', 'ecosystem', 'infrastructure', 'platform',
            'framework', 'integration', 'interface', 'api', 'service'
        ]
        system_count = sum(1 for word in system_words if word in answer_lower)
        score += min(25, system_count * 3)
        
        # Holistic thinking
        holistic_words = [
            'holistic', 'comprehensive', 'end-to-end', 'overall', 'complete',
            'entire', 'whole', 'full picture', 'big picture', 'overview'
        ]
        holistic_count = sum(1 for word in holistic_words if word in answer_lower)
        score += min(20, holistic_count * 4)
        
        # Dependencies and relationships
        dependency_words = [
            'dependency', 'relationship', 'connection', 'interaction', 'integration',
            'coupling', 'cohesion', 'interface', 'contract', 'protocol'
        ]
        dep_count = sum(1 for word in dependency_words if word in answer_lower)
        score += min(25, dep_count * 5)
        
        # Impact analysis
        impact_words = [
            'impact', 'effect', 'consequence', 'result', 'outcome', 'implication',
            'ripple effect', 'downstream', 'upstream', 'cascading'
        ]
        impact_count = sum(1 for word in impact_words if word in answer_lower)
        score += min(30, impact_count * 6)
        
        return min(100, score)
    
    def _ai_deep_analysis(self, question_data: Dict, answer: str, role: str) -> Dict:
        """AI analysis specifically calibrated for top-tier standards"""
        prompt = f"""
        Perform top-tier tech company level evaluation of this interview response with extreme rigor:
        
        Question Category: {question_data.get('category', 'General')}
        Question: {question_data.get('question', 'N/A')}
        Role: {role}
        Answer: {answer}
        
        Evaluate against top-tier hiring standards and return JSON with:
        - calibrated_score: 1-10 (10 = hire at senior+ level, 8-9 = hire at mid-senior, 6-7 = hire at mid, <6 = no hire)
        - technical_depth_rating: 1-10 (depth of technical knowledge demonstrated)
        - problem_solving_sophistication: 1-10 (sophistication of approach)
        - communication_clarity: 1-10 (clarity and structure of explanation)
        - innovation_factor: 1-10 (creative and innovative thinking)
        - readiness_indicators: list of positive indicators for top-tier readiness
        - red_flags: list of concerning aspects that would concern interviewers
        - missing_elements: what's missing for a strong response
        - standout_qualities: exceptional aspects of the response
        - improvement_priority: top 3 areas for improvement
        - comparable_level: estimated current level (Junior, Mid, Senior, Staff+)
        """
        
        try:
            response = self.bedrock.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 1200,
                    'messages': [{'role': 'user', 'content': prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            analysis_text = result['content'][0]['text']
            
            try:
                return json.loads(analysis_text)
            except:
                return self._fallback_analysis(answer)
                
        except Exception as e:
            return self._fallback_analysis(answer)
    
    def _make_hiring_decision(self, weighted_score: float, ai_analysis: Dict) -> Dict:
        """Make hiring decision"""
        
        if weighted_score >= 85 and ai_analysis.get('calibrated_score', 0) >= 9:
            decision = "STRONG HIRE"
            level = "Senior/Staff Level"
            confidence = "High"
        elif weighted_score >= 75 and ai_analysis.get('calibrated_score', 0) >= 8:
            decision = "HIRE"
            level = "Mid-Senior Level"
            confidence = "Medium-High"
        elif weighted_score >= 65 and ai_analysis.get('calibrated_score', 0) >= 6:
            decision = "LEAN HIRE"
            level = "Mid Level"
            confidence = "Medium"
        elif weighted_score >= 50:
            decision = "LEAN NO HIRE"
            level = "Below Standards"
            confidence = "Medium"
        else:
            decision = "NO HIRE"
            level = "Significant Gap"
            confidence = "High"
        
        return {
            'decision': decision,
            'estimated_level': level,
            'confidence': confidence,
            'reasoning': self._get_decision_reasoning(weighted_score, ai_analysis)
        }
    
    def _generate_detailed_feedback(self, tech_score, prob_score, comm_score, innov_score, lead_score, sys_score, ai_analysis) -> str:
        """Generate comprehensive feedback"""
        
        avg_score = (tech_score + prob_score + comm_score + innov_score + lead_score + sys_score) / 6
        
        feedback_parts = []
        
        if avg_score >= 85:
            feedback_parts.append("Exceptional performance demonstrating senior+ level expertise suitable for top-tier roles.")
        elif avg_score >= 75:
            feedback_parts.append("Strong performance showing solid competency with room for senior growth.")
        elif avg_score >= 65:
            feedback_parts.append("Good foundation with potential for top-tier roles after targeted improvement.")
        else:
            feedback_parts.append("Significant development needed to meet top-tier hiring standards.")
        
        # Specific dimension feedback
        if tech_score < 70:
            feedback_parts.append("Technical depth needs significant enhancement for top-tier standards.")
        if prob_score < 70:
            feedback_parts.append("Problem-solving approach requires more structured and comprehensive methodology.")
        if comm_score < 70:
            feedback_parts.append("Communication clarity and structure need improvement for senior technical roles.")
        
        return " ".join(feedback_parts)
    
    def _generate_improvement_roadmap(self, score: float, ai_analysis: Dict) -> List[str]:
        """Generate specific improvement roadmap"""
        
        roadmap = []
        
        if score < 85:
            roadmap.extend([
                "Deep dive into system design patterns and distributed systems architecture",
                "Practice advanced algorithmic problems (LeetCode Hard+ level)",
                "Study top-tier company specific technologies and scale challenges"
            ])
        
        if score < 75:
            roadmap.extend([
                "Improve technical communication and explanation skills",
                "Build experience with large-scale system challenges",
                "Develop leadership and mentoring experience"
            ])
        
        if score < 65:
            roadmap.extend([
                "Strengthen fundamental computer science concepts",
                "Practice structured problem-solving approaches",
                "Build portfolio of complex technical projects"
            ])
        
        return roadmap[:6]
    
    def _assess_readiness(self, score: float, ai_analysis: Dict) -> str:
        """Assess overall readiness level"""
        
        calibrated_score = ai_analysis.get('calibrated_score', score/10)
        
        if calibrated_score >= 9:
            return "TOP-TIER READY - Senior Level"
        elif calibrated_score >= 8:
            return "TOP-TIER READY - Mid Level"
        elif calibrated_score >= 6:
            return "POTENTIAL - Needs Preparation"
        elif calibrated_score >= 4:
            return "SIGNIFICANT GAP - 6-12 months preparation needed"
        else:
            return "MAJOR GAP - 12+ months intensive preparation needed"
    
    def _generate_prep_recommendations(self, score: float, category: str) -> List[str]:
        """Generate specific interview preparation recommendations"""
        
        recommendations = []
        
        if category == 'system_design':
            recommendations.extend([
                "Study 'Designing Data-Intensive Applications' by Martin Kleppmann",
                "Practice system design problems from Grokking the System Design Interview",
                "Build and deploy a distributed system project"
            ])
        elif category == 'algorithmic_thinking':
            recommendations.extend([
                "Complete 200+ Leetcode problems (focus on Hard difficulty)",
                "Study 'Introduction to Algorithms' (CLRS)",
                "Practice whiteboard coding and time complexity analysis"
            ])
        elif category == 'behavioral_leadership':
            recommendations.extend([
                "Prepare STAR method examples for leadership scenarios",
                "Study leadership principles from top tech companies",
                "Practice articulating technical decisions and trade-offs"
            ])
        
        # General prep
        recommendations.extend([
            "Mock interviews with experienced engineers",
            "Study company-specific engineering blogs and case studies",
            "Build projects that demonstrate scale and complexity"
        ])
        
        return recommendations[:5]
    
    def _fallback_analysis(self, answer: str) -> Dict:
        """Fallback analysis when AI fails"""
        word_count = len(answer.split())
        
        return {
            'calibrated_score': min(8, word_count // 50),
            'technical_depth_rating': 6,
            'problem_solving_sophistication': 6,
            'communication_clarity': 7,
            'innovation_factor': 5,
            'readiness_indicators': ['Shows technical knowledge'],
            'red_flags': ['Limited depth in response'],
            'missing_elements': ['More specific examples needed'],
            'standout_qualities': 'Clear communication',
            'improvement_priority': ['Technical depth', 'Specific examples', 'System thinking'],
            'comparable_level': 'Mid'
        }
    
    def _get_decision_reasoning(self, score: float, ai_analysis: Dict) -> str:
        """Generate reasoning for hiring decision"""
        
        if score >= 85:
            return "Demonstrates exceptional technical depth, problem-solving sophistication, and communication skills expected at senior levels."
        elif score >= 75:
            return "Shows strong technical competency and problem-solving ability suitable for mid-senior roles."
        elif score >= 65:
            return "Has good foundation but needs improvement in technical depth and system thinking for top-tier standards."
        else:
            return "Significant gaps in technical knowledge, problem-solving approach, and communication clarity for top-tier roles."