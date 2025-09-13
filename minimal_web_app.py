from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Session storage
session_data = {}

@app.route('/')
def index():
    return render_template('interview.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    role = request.form.get('role', 'Software Engineer')
    
    # Mock candidate data (no external AI)
    candidate_data = {
        'name': 'Test Candidate',
        'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'SQL'],
        'experience_years': 3,
        'ats_score': 75,
        'technical_depth': 70,
        'leadership_score': 60
    }
    
    # Generate questions without external AI
    questions = generate_role_questions(role, 5)
    
    # Store in session
    global session_data
    session_data = {
        'candidate_data': candidate_data,
        'questions': questions,
        'role': role,
        'current_question': 0,
        'evaluations': []
    }
    
    return jsonify({
        'candidate_data': candidate_data,
        'readiness_score': 72.5,
        'total_questions': len(questions),
        'analysis_message': f'Resume analyzed for {role} | {len(questions)} questions generated | No external AI required'
    })

@app.route('/question')
def get_question():
    if not session_data or 'questions' not in session_data:
        return jsonify({'error': 'No active session'}), 400
    
    current = session_data['current_question']
    questions = session_data['questions']
    
    if current >= len(questions):
        return jsonify({'completed': True})
    
    question_data = questions[current]
    
    return jsonify({
        'question_data': question_data,
        'question_number': current + 1,
        'total_questions': len(questions),
        'progress': ((current + 1) / len(questions)) * 100
    })

@app.route('/answer', methods=['POST'])
def submit_answer():
    if not session_data or 'questions' not in session_data:
        return jsonify({'error': 'No active session'}), 400
    
    data = request.json
    answer = data.get('answer', '')
    
    if not answer:
        return jsonify({'error': 'No answer provided'}), 400
    
    current = session_data['current_question']
    question_data = session_data['questions'][current]
    role = session_data['role']
    
    # Basic evaluation without external AI
    evaluation = evaluate_answer_basic(question_data['question'], answer, role)
    
    session_data['evaluations'].append({
        'question_data': question_data,
        'answer': answer,
        'evaluation': evaluation,
        'timestamp': datetime.now().isoformat()
    })
    
    session_data['current_question'] += 1
    
    return jsonify({
        'evaluation': evaluation,
        'next_question': session_data['current_question'] < len(session_data['questions'])
    })

@app.route('/results')
def get_results():
    if not session_data or 'evaluations' not in session_data:
        return jsonify({'error': 'No completed interview'}), 400
    
    evaluations = session_data['evaluations']
    candidate_data = session_data['candidate_data']
    
    # Calculate scores
    overall_scores = [eval_data['evaluation']['overall_score'] for eval_data in evaluations]
    avg_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
    
    # Generate assessment
    if avg_score >= 80:
        final_assessment = {
            'level': 'STRONG - Senior Level',
            'readiness': 'Ready for Senior roles',
            'timeline': '2-4 weeks prep',
            'recommended_role': 'Senior Software Engineer',
            'confidence': 'High'
        }
    elif avg_score >= 70:
        final_assessment = {
            'level': 'GOOD - Mid-Senior Level',
            'readiness': 'Ready for Mid-Senior roles',
            'timeline': '6-8 weeks intensive prep',
            'recommended_role': 'Software Engineer',
            'confidence': 'Medium-High'
        }
    else:
        final_assessment = {
            'level': 'DEVELOPING',
            'readiness': 'Needs improvement',
            'timeline': '3-6 months preparation',
            'recommended_role': 'Junior Software Engineer',
            'confidence': 'Medium'
        }
    
    return jsonify({
        'performance_summary': {
            'overall_score': round(avg_score, 1),
            'final_assessment': final_assessment,
            'readiness_level': final_assessment['readiness']
        },
        'dimension_analysis': evaluations[0]['evaluation'] if evaluations else {},
        'detailed_evaluations': evaluations,
        'candidate_profile': candidate_data,
        'job_matches': [],
        'interview_metadata': {
            'total_questions': len(evaluations),
            'completion_time': datetime.now().isoformat(),
            'duration_minutes': 15,
            'difficulty_level': 'STANDARD'
        }
    })

def generate_role_questions(role: str, count: int = 5):
    """Generate role-specific questions"""
    
    question_templates = {
        "Software Engineer": [
            "Describe your experience with software development lifecycle.",
            "How do you approach debugging complex issues?",
            "Explain your understanding of object-oriented programming.",
            "What testing strategies do you use in your projects?",
            "How do you ensure code quality and maintainability?"
        ],
        "Frontend Developer": [
            "Describe your experience with modern JavaScript frameworks.",
            "How do you ensure cross-browser compatibility?",
            "Explain your approach to responsive web design.",
            "What tools do you use for frontend performance optimization?",
            "How do you handle state management in complex applications?"
        ],
        "Backend Developer": [
            "Describe your experience with API design and development.",
            "How do you handle database optimization?",
            "Explain your approach to system scalability.",
            "What security measures do you implement in backend systems?",
            "How do you handle error handling and logging?"
        ]
    }
    
    templates = question_templates.get(role, question_templates["Software Engineer"])
    questions = []
    
    for i, template in enumerate(templates[:count]):
        questions.append({
            "question": template,
            "category": "Technical",
            "difficulty": "intermediate"
        })
    
    return questions

def evaluate_answer_basic(question: str, answer: str, role: str):
    """Basic evaluation without external AI"""
    
    words = len(answer.split()) if answer else 0
    base_score = min(85, max(30, words * 1.5))
    
    technical_keywords = ["implement", "design", "develop", "test", "optimize", "scale", "maintain"]
    keyword_bonus = sum(5 for keyword in technical_keywords if keyword.lower() in answer.lower())
    
    final_score = min(100, base_score + keyword_bonus)
    
    return {
        'overall_score': int(final_score),
        'dimension_scores': {
            'technical_mastery': int(final_score),
            'problem_solving': max(0, int(final_score - 5)),
            'communication': min(100, words * 2),
            'innovation': max(0, int(final_score - 10)),
            'leadership': max(0, int(final_score - 15)),
            'system_thinking': max(0, int(final_score - 5))
        },
        'detailed_feedback': generate_feedback(final_score, words),
        'hiring_decision': {
            'decision': 'Hire' if final_score >= 65 else 'No Hire',
            'confidence': min(0.9, max(0.5, final_score / 100))
        }
    }

def generate_feedback(score: int, word_count: int):
    """Generate basic feedback"""
    if score >= 85:
        return "Excellent response with good technical depth and clear communication."
    elif score >= 70:
        return "Good response. Consider adding more specific examples and technical details."
    elif score >= 50:
        return "Adequate response. Focus on providing more comprehensive explanations."
    else:
        return "Response needs improvement. Provide more detailed technical explanations."

if __name__ == '__main__':
    print("Starting Minimal Interview Assistant")
    print("Visit: http://localhost:5002")
    print("No external AI dependencies required")
    app.run(debug=True, port=5002)