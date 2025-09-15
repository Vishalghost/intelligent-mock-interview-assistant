from flask import Flask, render_template, request, jsonify, send_file, session
from flask_wtf.csrf import CSRFProtect
import os
import json
import time
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
app.config['WTF_CSRF_ENABLED'] = os.getenv('WTF_CSRF_ENABLED', 'False').lower() == 'true'
app.config['SESSION_COOKIE_SECURE'] = False  # For local development
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize CSRF protection
csrf = CSRFProtect(app)

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
    """Check if file extension is allowed"""
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions and len(extension) <= 10

def validate_file_size(file):
    """Validate file size"""
    if hasattr(file, 'content_length') and file.content_length:
        return file.content_length <= app.config['MAX_CONTENT_LENGTH']
    return True

def get_session_id():
    """Get or create session ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_session_data(session_id):
    """Thread-safe session data retrieval"""
    with session_lock:
        return session_storage.get(session_id, {})

def set_session_data(session_id, data):
    """Thread-safe session data storage"""
    with session_lock:
        session_storage[session_id] = data

def extract_text_from_file(file_path):
    """Extract text from PDF or DOCX file"""
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
        else:
            return "Unsupported file format"
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def analyze_resume_simple(file_path, role):
    """Simple resume analysis without AI models"""
    text = extract_text_from_file(file_path)
    
    # Extract basic info
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    # Extract skills
    tech_skills = ['Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'AWS', 'Docker', 'Git']
    found_skills = [skill for skill in tech_skills if skill.lower() in text.lower()]
    
    # Calculate experience years
    year_pattern = r'\b(19|20)\d{2}\b'
    years = re.findall(year_pattern, text)
    experience_years = max(0, max([int(y) for y in years]) - min([int(y) for y in years])) if len(years) >= 2 else 2
    
    return {
        'candidate_info': {
            'name': 'Candidate',
            'email': emails[0] if emails else ''
        },
        'skills': found_skills,
        'professional_profile': {
            'experience_years': experience_years,
            'domain_expertise': 'Software Development',
            'seniority_level': 'Mid-level' if experience_years >= 3 else 'Junior'
        },
        'assessment_scores': {
            'ats_score': min(100, 50 + len(found_skills) * 5),
            'technical_depth': min(100, 40 + len(found_skills) * 8),
            'leadership_potential': min(100, 30 + experience_years * 10)
        }
    }

def generate_questions_simple(role, skills, experience_level):
    """Generate simple interview questions"""
    questions = [
        {
            "question": f"Tell me about your experience with {skills[0] if skills else 'programming'} and how you've used it in projects.",
            "category": "Technical",
            "expected_duration": 3
        },
        {
            "question": "Describe a challenging problem you solved and your approach to solving it.",
            "category": "Problem Solving", 
            "expected_duration": 4
        },
        {
            "question": f"How do you stay updated with the latest trends in {role.lower()}?",
            "category": "Learning",
            "expected_duration": 3
        }
    ]
    
    return {
        'questions': questions,
        'total_questions': len(questions),
        'estimated_duration': sum(q['expected_duration'] for q in questions)
    }

def evaluate_answer_simple(question, answer, role):
    """Simple answer evaluation"""
    word_count = len(answer.split()) if answer else 0
    
    # Basic scoring
    content_score = min(100, max(20, word_count * 2))
    technical_score = content_score + (10 if any(skill.lower() in answer.lower() for skill in ['implement', 'design', 'develop']) else 0)
    
    return {
        'overall_score': min(100, technical_score),
        'dimension_scores': {
            'technical_mastery': technical_score,
            'problem_solving': content_score,
            'communication': min(100, content_score + 10),
            'innovation': max(50, content_score - 10),
            'leadership': max(40, content_score - 20),
            'system_thinking': content_score
        },
        'detailed_feedback': f"Good response with {word_count} words. Consider adding more specific examples.",
        'hiring_recommendation': {
            'decision': 'Hire' if technical_score >= 70 else 'Consider',
            'confidence': min(0.95, technical_score / 100),
            'reasoning': 'Based on response quality and technical content.'
        }
    }

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 50MB.'}), 413

@app.route('/')
def index():
    return render_template('voice_interview.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    """Upload and analyze resume"""
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400
        
        file = request.files['resume']
        role = request.form.get('role', 'Software Engineer')
        
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_RESUME_EXTENSIONS):
            return jsonify({'error': 'Invalid file type. Only PDF and DOCX allowed.'}), 400
        
        if not validate_file_size(file):
            return jsonify({'error': 'File too large'}), 400
        
        # Save file securely
        filename = secure_filename(file.filename)
        if not filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        unique_filename = f"{filename.rsplit('.', 1)[0]}_{int(time.time())}.{filename.rsplit('.', 1)[1]}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(file_path)
        
        # Analyze resume
        analysis_result = analyze_resume_simple(file_path, role)
        
        # Store in session
        session_id = get_session_id()
        session_data = {
            'candidate_analysis': analysis_result,
            'role': role,
            'resume_file': unique_filename,
            'session_start': datetime.now().isoformat()
        }
        set_session_data(session_id, session_data)
        
        # Extract data for frontend
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
    """Start voice interview session"""
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
                'estimated_duration': questions_result.get('estimated_duration', 10),
                'first_question': questions[0] if questions else None,
                'role': role,
                'experience_level': experience_level
            }
        })
        
    except Exception as e:
        print(f"Interview start error: {e}")
        return jsonify({'error': 'Failed to start interview'}), 500

@app.route('/get_current_question', methods=['GET'])
def get_current_question():
    """Get current interview question"""
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
    """Process voice answer (simplified)"""
    try:
        session_id = get_session_id()
        session_data = get_session_data(session_id)
        
        # Initialize session data if not present
        if 'interview_questions' not in session_data:
            return jsonify({'error': 'No active interview session'}), 400
            
        if 'voice_evaluations' not in session_data:
            session_data['voice_evaluations'] = []
        
        # Get text answer instead of audio for simplicity
        answer_text = request.form.get('answer_text', 'Sample answer for demonstration')
        question_data = request.form.get('question_data', '{}')
        
        try:
            question_data = json.loads(question_data)
        except json.JSONDecodeError:
            question_data = {}
        
        # Evaluate answer
        evaluation_result = evaluate_answer_simple(
            question_data.get('question', ''),
            answer_text,
            session_data.get('role', 'Software Engineer')
        )
        
        # Mock voice metrics
        voice_metrics = {
            'clarity': 0.8,
            'confidence': 0.75,
            'pace': 'moderate',
            'duration_seconds': 45
        }
        
        # Store evaluation
        if 'voice_evaluations' not in session_data:
            session_data['voice_evaluations'] = []
            
        session_data['voice_evaluations'].append({
            'question_data': question_data,
            'answer': answer_text,
            'voice_metrics': voice_metrics,
            'evaluation': evaluation_result,
            'timestamp': datetime.now().isoformat()
        })
        
        # Move to next question
        session_data['current_question_index'] += 1
        set_session_data(session_id, session_data)
        
        return jsonify({
            'success': True,
            'transcription': {'text': answer_text, 'confidence': 0.9},
            'voice_metrics': voice_metrics,
            'evaluation': evaluation_result,
            'next_question_available': session_data['current_question_index'] < len(session_data['interview_questions']['questions'])
        })
        
    except Exception as e:
        print(f"Answer processing error: {e}")
        return jsonify({'error': 'Answer processing failed'}), 500

@app.route('/complete_voice_interview', methods=['POST'])
def complete_voice_interview():
    """Complete interview and generate report"""
    session_id = get_session_id()
    session_data = get_session_data(session_id)
    
    # Initialize voice_evaluations if not present
    if 'voice_evaluations' not in session_data:
        session_data['voice_evaluations'] = []
    
    try:
        evaluations = session_data['voice_evaluations']
        overall_scores = [eval_data['evaluation']['overall_score'] for eval_data in evaluations]
        avg_score = sum(overall_scores) / len(overall_scores)
        
        report = {
            'interview_summary': {
                'session_id': session_id,
                'completion_time': datetime.now().isoformat(),
                'total_questions': len(evaluations),
                'overall_score': round(avg_score, 1),
                'performance_level': 'Excellent' if avg_score >= 80 else 'Good' if avg_score >= 60 else 'Needs Improvement'
            },
            'candidate_profile': session_data.get('candidate_analysis', {}),
            'performance_analysis': {
                'overall_score': round(avg_score, 1),
                'final_assessment': {
                    'level': 'Ready for hire' if avg_score >= 70 else 'Needs improvement',
                    'readiness': 'High' if avg_score >= 80 else 'Medium',
                    'timeline': 'Immediate' if avg_score >= 80 else '2-4 weeks',
                    'confidence': 'High'
                }
            },
            'detailed_evaluations': evaluations,
            'job_recommendations': [
                {'title': 'Software Engineer', 'match_score': min(95, avg_score + 10), 'reasoning': 'Strong technical skills'}
            ]
        }
        
        session_data['final_report'] = report
        session_data['completion_time'] = datetime.now().isoformat()
        set_session_data(session_id, session_data)
        
        return jsonify({
            'success': True,
            'message': 'Interview completed successfully',
            'report': report
        })
        
    except Exception as e:
        print(f"Interview completion error: {e}")
        return jsonify({'error': 'Failed to complete interview'}), 500

if __name__ == '__main__':
    print("Starting Simple Voice Interview Assistant")
    print("=" * 50)
    print("Web Interface: http://localhost:5003")
    print("Upload resume -> Answer questions -> Get report")
    print("=" * 50)
    
    # Add report download route
    @app.route('/download_report')
    def download_report():
        """Download interview report"""
        session_id = get_session_id()
        session_data = get_session_data(session_id)
        
        # Create basic report if none exists
        if 'voice_evaluations' not in session_data:
            session_data['voice_evaluations'] = []
            
        # Generate report content
        report_content = "AI Voice Interview Report\n"
        report_content += "=" * 30 + "\n\n"
        report_content += f"Session ID: {session_id}\n"
        report_content += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Add evaluations
        for i, eval_data in enumerate(session_data.get('voice_evaluations', []), 1):
            report_content += f"\nQuestion {i}:\n"
            report_content += "-" * 20 + "\n"
            report_content += f"Question: {eval_data.get('question_data', {}).get('question', 'N/A')}\n"
            report_content += f"Answer: {eval_data.get('answer', 'N/A')}\n"
            report_content += f"Score: {eval_data.get('evaluation', {}).get('overall_score', 0)}/100\n"
            report_content += f"Feedback: {eval_data.get('evaluation', {}).get('detailed_feedback', 'N/A')}\n"
        
        # Create temporary file
        report_file = os.path.join(app.config['UPLOAD_FOLDER'], f'interview_report_{session_id[:8]}.txt')
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        return send_file(report_file, as_attachment=True, download_name='interview_report.txt')

    app.run(debug=True, port=5003, host='127.0.0.1')