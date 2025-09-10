from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('professional_interview.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    # Mock candidate data since resume parser has issues
    candidate_data = {
        'name': 'Test Candidate',
        'skills': ['Python', 'JavaScript', 'React'],
        'experience_years': 3,
        'ats_score': 75,
        'technical_depth': 70,
        'leadership_score': 60
    }
    
    return jsonify({
        'candidate_data': candidate_data,
        'readiness_score': 72.5,
        'total_questions': 3,
        'warning_level': 'extreme',
        'analysis_message': 'Mock Analysis Complete for Test Candidate | 3 skills identified | 3 years experience | ATS Score: 75/100'
    })

@app.route('/question')
def get_question():
    return jsonify({
        'question_data': {
            'question': 'Describe your experience with Python development.',
            'category': 'Technical',
            'difficulty': 'intermediate'
        },
        'question_number': 1,
        'total_questions': 3,
        'progress': 33.3
    })

@app.route('/answer', methods=['POST'])
def submit_answer():
    return jsonify({
        'evaluation': {
            'overall_score': 75,
            'dimension_scores': {
                'technical_mastery': 75,
                'problem_solving': 70,
                'communication': 80,
                'innovation': 65,
                'leadership': 60,
                'system_thinking': 70
            },
            'detailed_feedback': 'Good technical response with clear examples.',
            'hiring_decision': {
                'decision': 'Hire',
                'confidence': 0.75
            }
        },
        'next_question': False
    })

@app.route('/results')
def get_results():
    return jsonify({
        'performance_summary': {
            'overall_score': 75.0,
            'final_assessment': {
                'level': 'GOOD - Mid-Senior Level',
                'readiness': 'Ready for Mid-Senior roles',
                'timeline': '6-8 weeks intensive prep',
                'recommended_role': 'Software Engineer',
                'confidence': 'Medium-High'
            },
            'readiness_level': 'Ready for Mid-Senior roles'
        },
        'dimension_analysis': {
            'technical_mastery': 75,
            'problem_solving': 70,
            'communication': 80,
            'innovation': 65,
            'leadership': 60,
            'system_thinking': 70
        },
        'candidate_profile': {
            'name': 'Test Candidate',
            'skills': ['Python', 'JavaScript', 'React'],
            'experience_years': 3
        },
        'job_matches': [],
        'personalized_resources': {
            'learning_path': ['Advanced Python', 'System Design'],
            'recommended_courses': ['Python Mastery', 'Architecture Patterns']
        },
        'interview_metadata': {
            'total_questions': 1,
            'completion_time': '2025-01-10T09:00:00',
            'duration_minutes': 15,
            'difficulty_level': 'ADVANCED'
        }
    })

if __name__ == '__main__':
    print("Starting minimal app")
    app.run(debug=True, port=5002)