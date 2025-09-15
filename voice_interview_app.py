from flask import Flask, render_template, request, jsonify, send_file, session
from flask_wtf.csrf import CSRFProtect
import os
import json
import subprocess
import time
import uuid
import threading
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from dotenv import load_dotenv
import tempfile
import wave

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Security Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 52428800))  # 50MB
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['AUDIO_FOLDER'] = os.getenv('AUDIO_FOLDER', 'audio_uploads')
app.config['WTF_CSRF_ENABLED'] = os.getenv('WTF_CSRF_ENABLED', 'True').lower() == 'true'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)

# Allowed file extensions from environment
ALLOWED_RESUME_EXTENSIONS = set(os.getenv('ALLOWED_RESUME_EXTENSIONS', 'pdf,docx').split(','))
ALLOWED_AUDIO_EXTENSIONS = set(os.getenv('ALLOWED_AUDIO_EXTENSIONS', 'wav,mp3,webm,ogg').split(','))

# Thread-safe session storage
session_lock = threading.Lock()
session_storage = {}

# MCP Server integration
mcp_process = None

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

def start_huggingface_mcp_server():
    """Start Hugging Face MCP server"""
    global mcp_process
    try:
        mcp_process = subprocess.Popen(
            ['python', 'huggingface_mcp_server.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        print("Hugging Face MCP Server started successfully")
        time.sleep(3)  # Allow server to initialize
        return True
    except (FileNotFoundError, PermissionError, subprocess.SubprocessError) as e:
        print(f"Failed to start MCP server: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error starting MCP server: {e}")
        return False

def call_mcp_tool(tool_name, arguments):
    """Call Hugging Face MCP server tool"""
    global mcp_process
    try:
        if mcp_process is None or mcp_process.poll() is not None:
            print("Restarting MCP server...")
            if not start_huggingface_mcp_server():
                return {"error": "MCP server unavailable"}
        
        # Prepare MCP request with unique ID
        mcp_request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        # Send request
        request_json = json.dumps(mcp_request) + '\n'
        mcp_process.stdin.write(request_json)
        mcp_process.stdin.flush()
        
        # Read response
        response_line = mcp_process.stdout.readline().strip()
        if response_line:
            response = json.loads(response_line)
            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"]
                if content and len(content) > 0:
                    return json.loads(content[0]["text"])
            elif "error" in response:
                print(f"MCP Error: {response['error']}")
                return {"error": response["error"]}
        
        return {"error": "No response from MCP server"}
        
    except Exception as e:
        print(f"MCP call failed: {e}")
        return {"error": str(e)}

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 50MB.'}), 413

@app.route('/')
def index():
    return render_template('voice_interview.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    """Upload and analyze resume using Hugging Face models"""
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400
        
        file = request.files['resume']
        role = request.form.get('role', 'Software Engineer')
        
        # Validate file
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_RESUME_EXTENSIONS):
            return jsonify({'error': 'Invalid file type. Only PDF and DOCX allowed.'}), 400
        
        if not validate_file_size(file):
            return jsonify({'error': 'File too large'}), 400
        
        # Save file securely with unique name
        filename = secure_filename(file.filename)
        if not filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        # Add timestamp to prevent conflicts
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{int(time.time())}{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Ensure upload directory exists and is secure
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(file_path)
        
        # Analyze resume using Hugging Face MCP server
        print(f"Analyzing resume: {filename}")
        analysis_result = call_mcp_tool("analyze_resume_hf", {
            "file_path": file_path,
            "target_role": role
        })
        
        if "error" in analysis_result:
            return jsonify({'error': f'Resume analysis failed: {analysis_result["error"]}'}), 500
        
        # Store in thread-safe session
        session_id = get_session_id()
        session_data = {
            'candidate_analysis': analysis_result,
            'role': role,
            'resume_file': unique_filename,
            'session_start': datetime.now().isoformat()
        }
        set_session_data(session_id, session_data)
        
        # Extract key data for frontend
        candidate_info = analysis_result.get('candidate_info', {})
        skills = analysis_result.get('skills', [])
        assessment_scores = analysis_result.get('assessment_scores', {})
        
        return jsonify({
            'success': True,
            'message': f'Resume analyzed successfully using AI models',
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
        # Clean up uploaded file on error
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        return jsonify({'error': 'Resume analysis failed'}), 500

@app.route('/start_voice_interview', methods=['POST'])
def start_voice_interview():
    """Start voice-based interview session"""
    session_id = get_session_id()
    session_data = get_session_data(session_id)
    
    if 'candidate_analysis' not in session_data:
        return jsonify({'error': 'No resume analysis found. Please upload resume first.'}), 400
    
    data = request.get_json()
    role = data.get('role', session_data.get('role', 'Software Engineer'))
    
    try:
        # Generate questions using Hugging Face models
        print(f"Generating questions for {role}")
        candidate_analysis = session_data['candidate_analysis']
        skills = candidate_analysis.get('skills', [])
        experience_level = candidate_analysis.get('professional_profile', {}).get('seniority_level', 'intermediate').lower()
        
        questions_result = call_mcp_tool("generate_questions_hf", {
            "role": role,
            "skills": skills,
            "experience_level": experience_level
        })
        
        if "error" in questions_result:
            return jsonify({'error': f'Question generation failed: {questions_result["error"]}'}), 500
        
        # Update session data
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
            'message': f'Voice interview started with {len(questions)} AI-generated questions',
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
    """Upload and process voice answer"""
    try:
        session_id = get_session_id()
        session_data = get_session_data(session_id)
        
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        if 'interview_questions' not in session_data:
            return jsonify({'error': 'No active interview session'}), 400
        
        audio_file = request.files['audio']
        question_data = request.form.get('question_data', '{}')
        
        # Validate audio file
        if not audio_file or not audio_file.filename:
            return jsonify({'error': 'Invalid audio file'}), 400
        
        if not allowed_file(audio_file.filename, ALLOWED_AUDIO_EXTENSIONS):
            return jsonify({'error': 'Invalid audio file type'}), 400
        
        if not validate_file_size(audio_file):
            return jsonify({'error': 'Audio file too large'}), 400
        
        try:
            question_data = json.loads(question_data)
        except json.JSONDecodeError:
            question_data = {}
        
        # Save audio file securely
        audio_filename = f"answer_{session_id}_{int(time.time())}_{secure_filename(audio_file.filename)}"
        audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
        
        # Ensure audio directory exists
        os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)
        audio_file.save(audio_path)
        
        try:
            # Process voice using Hugging Face models
            print(f"Processing voice answer: {audio_filename}")
            voice_result = call_mcp_tool("process_voice_answer", {
                "audio_file": audio_path,
                "question": question_data.get('question', '')
            })
            
            if "error" in voice_result:
                return jsonify({'error': f'Voice processing failed: {voice_result["error"]}'}), 500
            
            # Get transcription
            transcription = voice_result.get('transcription', {})
            voice_metrics = voice_result.get('voice_metrics', {})
            
            # Evaluate answer using AI
            print(f"Evaluating answer with AI...")
            evaluation_result = call_mcp_tool("evaluate_answer_hf", {
                "question": question_data.get('question', ''),
                "answer": transcription.get('text', ''),
                "role": session_data.get('role', 'Software Engineer'),
                "voice_metrics": voice_metrics
            })
            
            if "error" in evaluation_result:
                return jsonify({'error': f'Answer evaluation failed: {evaluation_result["error"]}'}), 500
            
            # Store evaluation
            session_data['voice_evaluations'].append({
                'question_data': question_data,
                'audio_file': audio_filename,
                'transcription': transcription,
                'voice_metrics': voice_metrics,
                'evaluation': evaluation_result,
                'timestamp': datetime.now().isoformat()
            })
            
            # Move to next question
            session_data['current_question_index'] += 1
            set_session_data(session_id, session_data)
            
            # Clean up audio file
            try:
                os.remove(audio_path)
            except OSError:
                pass
            
            return jsonify({
                'success': True,
                'transcription': transcription,
                'voice_metrics': voice_metrics,
                'evaluation': evaluation_result,
                'next_question_available': session_data['current_question_index'] < len(session_data['interview_questions']['questions'])
            })
            
        except Exception as e:
            print(f"Voice processing error: {e}")
            # Clean up audio file on error
            try:
                if 'audio_path' in locals() and os.path.exists(audio_path):
                    os.remove(audio_path)
            except OSError:
                pass
            return jsonify({'error': 'Voice processing failed'}), 500
    
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/complete_voice_interview', methods=['POST'])
def complete_voice_interview():
    """Complete voice interview and generate comprehensive report"""
    session_id = get_session_id()
    session_data = get_session_data(session_id)
    
    if 'voice_evaluations' not in session_data or not session_data['voice_evaluations']:
        return jsonify({'error': 'No interview data available'}), 400
    
    try:
        # Generate comprehensive report using Hugging Face models
        print(f"Generating comprehensive interview report...")
        session_id = f"voice_interview_{int(time.time())}"
        
        report_result = call_mcp_tool("complete_interview_hf", {
            "session_id": session_id
        })
        
        if "error" in report_result:
            return jsonify({'error': f'Report generation failed: {report_result["error"]}'}), 500
        
        # Store final report
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

@app.route('/download_voice_report')
def download_voice_report():
    """Download comprehensive voice interview report"""
    session_id = get_session_id()
    session_data = get_session_data(session_id)
    
    if 'final_report' not in session_data:
        return jsonify({'error': 'No completed interview report available'}), 400
    
    try:
        report = session_data['final_report']
        
        # Generate detailed text report
        report_content = generate_voice_report_content(report)
        
        # Save to secure file with session ID
        safe_session_id = session_id.replace('-', '')[:8]
        filename = f"voice_interview_report_{safe_session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except (IOError, OSError, PermissionError) as e:
        print(f"File operation error: {e}")
        return jsonify({'error': 'Report generation failed'}), 500
    except Exception as e:
        print(f"Report generation error: {e}")
        return jsonify({'error': 'Report generation failed'}), 500

def generate_voice_report_content(report: dict) -> str:
    """Generate comprehensive voice interview report content"""
    content = f"""
=== AI-POWERED VOICE INTERVIEW ASSESSMENT REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Powered by: Hugging Face AI Models + Amazon Q CLI Integration

INTERVIEW SUMMARY:
Session ID: {report.get('interview_summary', {}).get('session_id', 'N/A')}
Completion Time: {report.get('interview_summary', {}).get('completion_time', 'N/A')}
Total Questions: {report.get('interview_summary', {}).get('total_questions', 0)}
Overall Score: {report.get('interview_summary', {}).get('overall_score', 0)}/100
Performance Level: {report.get('interview_summary', {}).get('performance_level', 'N/A')}

CANDIDATE PROFILE:
"""
    
    candidate = report.get('candidate_profile', {})
    candidate_info = candidate.get('candidate_info', {})
    
    content += f"""Name: {candidate_info.get('name', 'N/A')}
Email: {candidate_info.get('email', 'N/A')}
Experience: {candidate.get('professional_profile', {}).get('experience_years', 0)} years
Domain: {candidate.get('professional_profile', {}).get('domain_expertise', 'N/A')}
Seniority Level: {candidate.get('professional_profile', {}).get('seniority_level', 'N/A')}

SKILLS ANALYSIS:
Total Skills Identified: {len(candidate.get('skills', []))}
Skills: {', '.join(candidate.get('skills', []))}

ASSESSMENT SCORES:
ATS Score: {candidate.get('assessment_scores', {}).get('ats_score', 0)}/100
Technical Depth: {candidate.get('assessment_scores', {}).get('technical_depth', 0)}/100
Leadership Potential: {candidate.get('assessment_scores', {}).get('leadership_potential', 0)}/100

PERFORMANCE ANALYSIS:
"""
    
    performance = report.get('performance_analysis', {})
    dimension_scores = performance.get('dimension_scores', {})
    
    content += f"""Overall Score: {performance.get('overall_score', 0)}/100

DIMENSION BREAKDOWN:
"""
    
    for dimension, score in dimension_scores.items():
        content += f"{dimension.replace('_', ' ').title()}: {score}/100\n"
    
    final_assessment = performance.get('final_assessment', {})
    content += f"""
FINAL ASSESSMENT:
Level: {final_assessment.get('level', 'N/A')}
Readiness: {final_assessment.get('readiness', 'N/A')}
Timeline: {final_assessment.get('timeline', 'N/A')}
Confidence: {final_assessment.get('confidence', 'N/A')}

JOB RECOMMENDATIONS:
"""
    
    job_recs = report.get('job_recommendations', [])
    for i, job in enumerate(job_recs, 1):
        content += f"{i}. {job.get('title', 'N/A')} (Match: {job.get('match_score', 0)}%)\n"
        content += f"   Reasoning: {job.get('reasoning', 'N/A')}\n\n"
    
    content += f"""
LEARNING PATH RECOMMENDATIONS:
Priority Areas: {', '.join(report.get('learning_path', {}).get('priority_areas', []))}
Suggested Courses: {', '.join(report.get('learning_path', {}).get('suggested_courses', []))}
Timeline: {report.get('learning_path', {}).get('timeline', 'N/A')}

NEXT STEPS:
"""
    
    next_steps = report.get('next_steps', [])
    for i, step in enumerate(next_steps, 1):
        content += f"{i}. {step}\n"
    
    content += f"""
DETAILED QUESTION-BY-QUESTION ANALYSIS:
"""
    
    evaluations = report.get('detailed_evaluations', [])
    for i, eval_data in enumerate(evaluations, 1):
        evaluation = eval_data.get('evaluation', {})
        voice_metrics = eval_data.get('voice_metrics', {})
        
        content += f"""
Question {i}: {eval_data.get('question', 'N/A')}
Answer: {eval_data.get('answer', 'N/A')[:200]}...
Overall Score: {evaluation.get('overall_score', 0)}/100

Voice Analysis:
- Clarity: {voice_metrics.get('clarity', 0):.2f}
- Confidence: {voice_metrics.get('confidence', 0):.2f}
- Pace: {voice_metrics.get('pace', 'N/A')}
- Duration: {voice_metrics.get('duration_seconds', 0)} seconds

Dimension Scores:
"""
        
        dim_scores = evaluation.get('dimension_scores', {})
        for dim, score in dim_scores.items():
            content += f"- {dim.replace('_', ' ').title()}: {score}/100\n"
        
        content += f"""
Feedback: {evaluation.get('detailed_feedback', 'N/A')}
Hiring Recommendation: {evaluation.get('hiring_recommendation', {}).get('decision', 'N/A')}
Confidence: {evaluation.get('hiring_recommendation', {}).get('confidence', 0):.2f}
Reasoning: {evaluation.get('hiring_recommendation', {}).get('reasoning', 'N/A')}

"""
    
    content += f"""
=== END OF REPORT ===

This report was generated using advanced AI models including:
- Hugging Face Transformers for NLP and skill extraction
- Voice processing and speech recognition
- Multi-dimensional evaluation algorithms
- Amazon Q CLI integration for comprehensive analysis

For questions about this report, please contact the interview assessment team.
"""
    
    return content

if __name__ == '__main__':
    print("Starting AI-Powered Voice Interview Assistant")
    print("=" * 60)
    print("Features:")
    print("- Hugging Face AI Models for Resume Analysis")
    print("- Voice-Based Interview Questions")
    print("- Real-time Speech Processing")
    print("- Multi-Dimensional AI Evaluation")
    print("- Comprehensive Report Generation")
    print("- Amazon Q CLI Integration")
    print("=" * 60)
    print("Web Interface: http://localhost:5003")
    print("Upload resume -> Answer questions by voice -> Get AI report")
    print("")
    
    # Start Hugging Face MCP server
    print("Starting Hugging Face MCP Server...")
    if start_huggingface_mcp_server():
        print("MCP Server ready for AI processing")
    else:
        print("MCP Server failed to start - using fallback mode")
    
    print("")
    print("Ready for voice interviews!")
    
    # Start Flask app
    app.run(debug=False, port=5003, host='127.0.0.1')