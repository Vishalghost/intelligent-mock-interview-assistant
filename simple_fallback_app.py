from flask import Flask, render_template, request, jsonify, send_file, session
from flask_wtf.csrf import CSRFProtect
import os
import json
import uuid
import threading
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from dotenv import load_dotenv
import PyPDF2
from docx import Document
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Security Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 52428800))  # 50MB
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['AUDIO_FOLDER'] = os.getenv('AUDIO_FOLDER', 'audio_uploads')
app.config['WTF_CSRF_ENABLED'] = False  # Disable for simplicity

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_RESUME_EXTENSIONS = {'pdf', 'docx'}
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'webm', 'ogg'}

# Thread-safe session storage
session_lock = threading.Lock()
session_storage = {}

def allowed_file(filename, allowed_extensions):
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions

def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_session_data(session_id):
    with session_lock:
        return session_storage.get(session_id, {})

def set_session_data(session_id, data):
    with session_lock:
        session_storage[session_id] = data

def extract_text_from_file(file_path):
    try:
        if file_path.lower().endswith('.pdf'):
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        elif file_path.lower().endswith('.docx'):
            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def analyze_resume_simple(file_path, role):
    text = extract_text_from_file(file_path)
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    # Extract name (first line)
    lines = text.split('\n')
    name = lines[0].strip() if lines else "Candidate"
    
    # Extract skills
    tech_skills = ['Python', 'Java', 'JavaScript', 'React', 'Node.js', 'Angular', 'Vue',
                   'Django', 'Flask', 'Spring', 'Docker', 'Kubernetes', 'AWS', 'Azure',
                   'SQL', 'MongoDB', 'PostgreSQL', 'Git', 'Linux', 'HTML', 'CSS']
    
    found_skills = []
    text_lower = text.lower()
    for skill in tech_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    # Calculate experience years
    year_pattern = r'\b(19|20)\d{2}\b'
    years = re.findall(year_pattern, text)
    experience_years = max(0, max([int(y) for y in years]) - min([int(y) for y in years])) if len(years) >= 2 else 2
    
    return {
        "candidate_info": {
            "name": name,
            "email": emails[0] if emails else "",
            "phone": "",
            "location": ""
        },
        "skills": found_skills,
        "professional_profile": {
            "experience_years": experience_years,
            "domain_expertise": "Software Development",
            "seniority_level": "Mid-level" if experience_years >= 3 else "Junior"
        },
        "assessment_scores": {
            "ats_score": 75,
            "technical_depth": min(100, len(found_skills) * 10),
            "leadership_potential": 50
        },
        "target_role": role
    }

def generate_questions_simple(role, skills, experience_level):
    questions = [
        f"Tell me about your experience with {skills[0] if skills else 'programming'} and how you've used it in projects.",
        f"Describe a challenging {role.lower()} project you worked on and how you solved technical problems.",
        "How do you approach debugging and troubleshooting issues in your code?",
        "Explain your understanding of software development best practices.",
        "Tell me about a time when you had to learn a new technology quickly."
    ]
    
    return {
        "role": role,
        "questions": questions,
        "total_questions": len(questions),
        "experience_level": experience_level,
        "estimated_duration": 20
    }

@app.route('/')
def index():
    return render_template('voice_interview.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400
        
        file = request.files['resume']
        role = request.form.get('role', 'Software Engineer')
        
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_RESUME_EXTENSIONS):
            return jsonify({'error': 'Invalid file type. Only PDF and DOCX allowed.'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Analyze resume
        analysis_result = analyze_resume_simple(file_path, role)
        
        # Store in session
        session_id = get_session_id()
        session_data = {
            'candidate_analysis': analysis_result,
            'role': role,
            'resume_file': filename,
            'session_start': datetime.now().isoformat()
        }
        set_session_data(session_id, session_data)
        
        candidate_info = analysis_result.get('candidate_info', {})
        skills = analysis_result.get('skills', [])
        assessment_scores = analysis_result.get('assessment_scores', {})
        
        return jsonify({
            'success': True,
            'message': 'Resume analyzed successfully',
            'candidate_data': {
                'name': candidate_info.get('name', 'Candidate'),
                'email': candidate_info.get('email', ''),
                'skills': skills,
                'experience_years': analysis_result.get('professional_profile', {}).get('experience_years', 0),
                'ats_score': assessment_scores.get('ats_score', 75),
                'technical_depth': assessment_scores.get('technical_depth', 60),
                'leadership_score': assessment_scores.get('leadership_potential', 40)
            },
            'analysis_summary': {
                'total_skills': len(skills),
                'domain': analysis_result.get('professional_profile', {}).get('domain_expertise', 'Software Development'),
                'seniority': analysis_result.get('professional_profile', {}).get('seniority_level', 'Mid-level')
            }
        })
        
    except Exception as e:
        print(f"Resume analysis error: {e}")
        return jsonify({'error': 'Resume analysis failed'}), 500

@app.route('/start_voice_interview', methods=['POST'])
def start_voice_interview():
    session_id = get_session_id()
    session_data = get_session_data(session_id)
    
    if 'candidate_analysis' not in session_data:
        return jsonify({'error': 'No resume analysis found. Please upload resume first.'}), 400
    
    data = request.get_json()
    role = data.get('role', session_data.get('role', 'Software Engineer'))
    
    try:
        candidate_analysis = session_data['candidate_analysis']
        skills = candidate_analysis.get('skills', [])
        experience_level = candidate_analysis.get('professional_profile', {}).get('seniority_level', 'intermediate').lower()
        
        questions_result = generate_questions_simple(role, skills, experience_level)
        
        session_data.update({
            'interview_questions': questions_result,
            'current_question_index': 0,
            'interview_start': datetime.now().isoformat(),
            'voice_evaluations': []
        })
        set_session_data(session_id, session_data)
        
        questions = questions_result.get('questions', [])
        
        return jsonify({
            'success': True,
            'message': f'Voice interview started with {len(questions)} questions',
            'interview_data': {
                'total_questions': len(questions),
                'estimated_duration': questions_result.get('estimated_duration', 20),
                'first_question': questions[0] if questions else None,
                'role': role,
                'experience_level': experience_level
            }
        })
        
    except Exception as e:
        print(f"Interview start error: {e}")
        return jsonify({'error': f'Failed to start interview: {str(e)}'}), 500

@app.route('/get_current_question', methods=['GET'])
def get_current_question():
    session_id = get_session_id()
    session_data = get_session_data(session_id)
    
    if 'interview_questions' not in session_data:
        return jsonify({'error': 'No active interview session'}), 400
    
    current_index = session_data.get('current_question_index', 0)
    questions = session_data['interview_questions'].get('questions', [])
    
    if current_index >= len(questions):
        return jsonify({
            'completed': True,
            'message': 'Interview completed successfully'
        })
    
    current_question = questions[current_index]
    
    return jsonify({
        'question': current_question,
        'question_number': current_index + 1,
        'total_questions': len(questions),
        'progress': ((current_index + 1) / len(questions)) * 100
    })

@app.route('/upload_voice_answer', methods=['POST'])
def upload_voice_answer():
    try:
        session_id = get_session_id()
        session_data = get_session_data(session_id)
        
        # For demo purposes, simulate voice processing
        question_data = json.loads(request.form.get('question_data', '{}'))
        
        # Simulate transcription and evaluation
        transcription = {
            "text": "This is a simulated transcription of the voice answer.",
            "confidence": 0.85,
            "word_count": 8
        }
        
        voice_metrics = {
            "clarity": 0.8,
            "confidence": 0.75,
            "pace": "moderate",
            "duration_seconds": 30
        }
        
        evaluation = {
            "overall_score": 75,
            "dimension_scores": {
                "technical_mastery": 70,
                "problem_solving": 75,
                "communication": 80,
                "innovation": 65,
                "leadership": 60,
                "system_thinking": 70
            },
            "detailed_feedback": "Good response with clear communication. Consider adding more technical details.",
            "hiring_recommendation": {
                "decision": "Hire",
                "confidence": 0.75,
                "reasoning": "Solid performance across dimensions"
            }
        }
        
        # Store evaluation
        session_data['voice_evaluations'].append({
            'question_data': question_data,
            'transcription': transcription,
            'voice_metrics': voice_metrics,
            'evaluation': evaluation,
            'timestamp': datetime.now().isoformat()
        })
        
        # Move to next question
        session_data['current_question_index'] += 1
        set_session_data(session_id, session_data)
        
        return jsonify({
            'success': True,
            'transcription': transcription,
            'voice_metrics': voice_metrics,
            'evaluation': evaluation,
            'next_question_available': session_data['current_question_index'] < len(session_data['interview_questions']['questions'])
        })
        
    except Exception as e:
        print(f"Voice processing error: {e}")
        return jsonify({'error': 'Voice processing failed'}), 500

@app.route('/complete_voice_interview', methods=['POST'])
def complete_voice_interview():
    session_id = get_session_id()
    session_data = get_session_data(session_id)
    
    if 'voice_evaluations' not in session_data or not session_data['voice_evaluations']:
        return jsonify({'error': 'No interview data available'}), 400
    
    try:
        evaluations = session_data['voice_evaluations']
        candidate_analysis = session_data.get('candidate_analysis', {})
        
        # Calculate averages
        overall_scores = [eval_data['evaluation']['overall_score'] for eval_data in evaluations]
        avg_score = sum(overall_scores) / len(overall_scores)
        
        report_result = {
            'interview_summary': {
                'session_id': session_id,
                'completion_time': datetime.now().isoformat(),
                'total_questions': len(evaluations),
                'overall_score': round(avg_score, 1),
                'performance_level': 'Good' if avg_score >= 70 else 'Needs Improvement'
            },
            'candidate_profile': candidate_analysis,
            'performance_analysis': {
                'overall_score': round(avg_score, 1),
                'dimension_scores': {
                    'technical_mastery': 70,
                    'problem_solving': 75,
                    'communication': 80,
                    'innovation': 65,
                    'leadership': 60,
                    'system_thinking': 70
                },
                'final_assessment': {
                    'level': 'Mid-level',
                    'readiness': 'Ready for interviews',
                    'timeline': '2-4 weeks',
                    'confidence': 'High'
                }
            },
            'job_recommendations': [
                {
                    'title': f"{session_data.get('role', 'Software Engineer')}",
                    'match_score': min(90, int(avg_score)),
                    'reasoning': 'Strong technical skills and good communication'
                }
            ],
            'learning_path': {
                'priority_areas': ['Technical depth', 'Communication skills'],
                'suggested_courses': ['Advanced programming', 'Public speaking'],
                'timeline': '3-6 months'
            },
            'next_steps': [
                'Practice more technical questions',
                'Improve communication clarity',
                'Build portfolio projects'
            ],
            'detailed_evaluations': evaluations
        }
        
        session_data['final_report'] = report_result
        session_data['completion_time'] = datetime.now().isoformat()
        set_session_data(session_id, session_data)
        
        return jsonify({
            'success': True,
            'message': 'Voice interview completed successfully',
            'report': report_result
        })
        
    except Exception as e:
        print(f"Interview completion error: {e}")
        return jsonify({'error': f'Failed to complete interview: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Simple Voice Interview Assistant")
    print("=" * 50)
    print("Features:")
    print("- Resume Analysis")
    print("- Voice Interview Questions")
    print("- Simulated AI Evaluation")
    print("- Report Generation")
    print("=" * 50)
    print("Web Interface: http://localhost:5003")
    print("")
    
    app.run(debug=True, port=5003, host='127.0.0.1')