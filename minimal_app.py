from flask import Flask, render_template, request, jsonify
import os
from optimized_deepseek import OptimizedDeepSeekAI

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize DeepSeek AI
ai_engine = OptimizedDeepSeekAI()
print(f"DeepSeek API Status: {'ENABLED' if ai_engine.use_ai else 'DISABLED'}")

@app.route('/')
def index():
    return render_template('professional_interview.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    role = request.form.get('role', 'Software Engineer')
    
    # Mock candidate data
    candidate_data = {
        'name': 'Test Candidate',
        'skills': ['Python', 'JavaScript', 'React'],
        'experience_years': 3,
        'ats_score': 75,
        'technical_depth': 70,
        'leadership_score': 60
    }
    
    # Generate real questions using DeepSeek API
    ai_resume_data = {
        'skills': candidate_data['skills'],
        'experience_years': candidate_data['experience_years'],
        'name': candidate_data['name']
    }
    
    questions = ai_engine.generate_questions(ai_resume_data, role)
    
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
        'warning_level': 'extreme',
        'analysis_message': f'DeepSeek API Analysis | {len(questions)} questions generated | Role: {role}'
    })

session_data = {}

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
    
    # Real DeepSeek API evaluation
    evaluation = ai_engine.evaluate_answer(
        question_data['question'], answer, role
    )
    
    session_data['evaluations'].append({
        'question_data': question_data,
        'answer': answer,
        'evaluation': evaluation
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
    
    # Calculate real scores from DeepSeek evaluations
    overall_scores = [eval_data['evaluation']['overall_score'] for eval_data in evaluations]
    avg_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
    
    # Generate assessment based on real scores
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
        'dimension_analysis': evaluations[0]['evaluation']['dimension_scores'] if evaluations else {},
        'detailed_evaluations': evaluations,
        'candidate_profile': candidate_data,
        'job_matches': [],
        'personalized_resources': {
            'learning_path': ['Advanced Python', 'System Design'],
            'recommended_courses': ['Python Mastery', 'Architecture Patterns']
        },
        'interview_metadata': {
            'total_questions': len(evaluations),
            'completion_time': '2025-01-10T09:00:00',
            'duration_minutes': 15,
            'difficulty_level': 'ADVANCED'
        }
    })

if __name__ == '__main__':
    print("Starting minimal app")
    app.run(debug=True, port=5002)