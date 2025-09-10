from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from extreme_questions import ExtremeQuestions
from advanced_evaluator import AdvancedEvaluator
from resources_generator import ResourcesGenerator
from enhanced_resume_parser import EnhancedResumeParser
from job_matcher import JobMatcher
from optimized_deepseek import OptimizedDeepSeekAI
from report_generator import ReportGenerator
from voice_transcriber import VoiceTranscriber

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Professional components
resume_parser = EnhancedResumeParser()
extreme_questions = ExtremeQuestions()
advanced_evaluator = AdvancedEvaluator()
resources_generator = ResourcesGenerator()
job_matcher = JobMatcher()
# Initialize DeepSeek AI with API
ai_engine = OptimizedDeepSeekAI()
ai_engine.toggle_ai(True)  # Enable AI API usage
voice_transcriber = VoiceTranscriber()
print(f"DeepSeek AI initialized - API Status: {'ENABLED' if ai_engine.use_ai else 'DISABLED'}")
print(f"Voice transcription: {'ENABLED' if voice_transcriber.model else 'DISABLED'}")
report_generator = ReportGenerator()

# Session storage
professional_session = {}

@app.route('/')
def index():
    return render_template('professional_interview.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    role = request.form.get('role', 'Software Engineer')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.lower().endswith(('.pdf', '.docx')):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Parse resume with enhanced parser
            candidate_data = resume_parser.parse_resume(filepath)
            
            # Enhance with DeepSeek AI analysis
            try:
                resume_text = resume_parser.extract_text(filepath)
                ai_analysis = ai_engine.analyze_resume(resume_text)
                if ai_analysis:
                    # Merge AI analysis with parsed data
                    for key, value in ai_analysis.items():
                        if key not in candidate_data or not candidate_data[key]:
                            candidate_data[key] = value
                    print(f" AI-enhanced resume analysis completed")
                else:
                    print(f" AI analysis unavailable, using parser data only")
            except Exception as e:
                print(f" AI analysis failed: {e}")
            
            # Check readiness
            readiness_score = (candidate_data['ats_score'] + candidate_data['technical_depth']) / 2
            
            # Prepare skills data for AI question generation
            skills_for_ai = candidate_data.get('skills', [])
            if isinstance(skills_for_ai, dict):
                skills_for_ai = skills_for_ai.get('all_skills', [])
            
            # Create AI-compatible resume data
            ai_resume_data = {
                'skills': skills_for_ai,
                'experience_years': candidate_data.get('experience_years', 0),
                'name': candidate_data.get('name', 'Candidate')
            }
            
            # Generate AI questions using DeepSeek API
            print(f" Generating questions for {role} with DeepSeek API...")
            ai_questions = ai_engine.generate_questions(ai_resume_data, role)
            print(f" Generated {len(ai_questions)} questions")
            
            # Use AI-generated questions with fallback
            if ai_questions and len(ai_questions) > 0:
                all_questions = ai_questions[:5]  # Limit to 5 high-quality questions
            else:
                # Fallback to extreme questions if AI fails
                extreme_qs = extreme_questions.generate_extreme_questions(candidate_data, role)
                all_questions = extreme_qs[:3]
            
            professional_session.update({
                'candidate_data': candidate_data,
                'questions': all_questions,
                'role': role,
                'current_question': 0,
                'evaluations': [],
                'readiness_score': readiness_score,
                'start_time': datetime.now().isoformat()
            })
            
            # Create detailed response message with AI enhancement indicator
            skills_count = candidate_data.get('skills', {}).get('total_count', 0) if isinstance(candidate_data.get('skills'), dict) else len(candidate_data.get('skills', []))
            ai_enhanced = " AI-Enhanced" if ai_analysis else " Parser-Based"
            message_parts = [
                f" {ai_enhanced} Analysis Complete for {candidate_data.get('name', 'Candidate')}",
                f" {skills_count} skills identified",
                f"⏱ {candidate_data.get('experience_years', 0)} years experience",
                f" ATS Score: {candidate_data.get('ats_score', 0)}/100"
            ]
            
            return jsonify({
                'candidate_data': candidate_data,
                'readiness_score': readiness_score,
                'total_questions': len(all_questions),
                'warning_level': 'extreme' if readiness_score >= 60 else 'preparation_needed',
                'analysis_message': ' | '.join(message_parts)
            })
            
        except Exception as e:
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/question')
def get_question():
    if 'questions' not in professional_session:
        return jsonify({'error': 'No active session'}), 400
    
    current = professional_session['current_question']
    questions = professional_session['questions']
    
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
    # Handle both text and audio input
    if 'audio' in request.files:
        # Voice input
        audio_file = request.files['audio']
        if audio_file:
            try:
                audio_data = audio_file.read()
                answer = voice_transcriber.transcribe_audio_data(audio_data)
                if not answer:
                    return jsonify({'error': 'Voice transcription failed'}), 400
                print(f" Transcribed: {answer[:100]}...")
            except Exception as e:
                return jsonify({'error': f'Audio processing failed: {str(e)}'}), 400
        else:
            return jsonify({'error': 'No audio data received'}), 400
    else:
        # Fallback text input (should not be used in voice-only mode)
        data = request.json
        answer = data.get('answer', '')
        if not answer:
            return jsonify({'error': 'No answer provided'}), 400
    
    if 'questions' not in professional_session:
        return jsonify({'error': 'No active session'}), 400
    
    current = professional_session['current_question']
    
    if current >= len(professional_session['questions']):
        return jsonify({'error': 'No more questions'}), 400
    
    question_data = professional_session['questions'][current]
    role = professional_session['role']
    candidate_data = professional_session['candidate_data']
    
    # AI evaluation using DeepSeek API
    print(f" Evaluating answer with DeepSeek API...")
    evaluation = ai_engine.evaluate_answer(
        question_data['question'], answer, role
    )
    print(f" Evaluation complete - Score: {evaluation.get('overall_score', 0)}/100")
    
    professional_session['evaluations'].append({
        'question_data': question_data,
        'answer': answer,
        'evaluation': evaluation,
        'timestamp': datetime.now().isoformat()
    })
    
    professional_session['current_question'] += 1
    
    return jsonify({
        'evaluation': evaluation,
        'next_question': professional_session['current_question'] < len(professional_session['questions'])
    })

@app.route('/results')
def get_results():
    if 'evaluations' not in professional_session:
        return jsonify({'error': 'No completed interview'}), 400
    
    evaluations = professional_session['evaluations']
    candidate_data = professional_session['candidate_data']
    
    # Calculate scores
    overall_scores = [eval_data['evaluation']['overall_score'] for eval_data in evaluations]
    avg_score = sum(overall_scores) / len(overall_scores)
    
    # Generate final assessment
    final_assessment = generate_final_assessment(avg_score, evaluations)
    
    # Calculate dimension averages
    dimension_averages = calculate_dimension_averages(evaluations)
    
    # Generate comprehensive resources
    combined_evaluation = {
        'overall_score': avg_score,
        'dimension_scores': dimension_averages,
        'hiring_decision': final_assessment,
        'improvement_areas': identify_improvement_areas(evaluations)
    }
    
    resources = resources_generator.generate_personalized_resources(
        combined_evaluation, candidate_data, professional_session['role']
    )
    
    # Job matching for high performers
    jobs = []
    if avg_score >= 70:
        jobs = job_matcher.fetch_jobs(
            final_assessment['recommended_role'], 
            candidate_data['skills'], 
            min_score=70
        )
    
    results = {
        'performance_summary': {
            'overall_score': round(avg_score, 1),
            'final_assessment': final_assessment,
            'readiness_level': final_assessment['readiness']
        },
        'dimension_analysis': dimension_averages,
        'detailed_evaluations': evaluations,
        'candidate_profile': candidate_data,
        'job_matches': jobs[:10],
        'personalized_resources': resources,
        'interview_metadata': {
            'total_questions': len(evaluations),
            'completion_time': datetime.now().isoformat(),
            'duration_minutes': calculate_duration(),
            'difficulty_level': 'ADVANCED'
        }
    }
    
    return jsonify(results)

@app.route('/download-report')
def download_report():
    if 'evaluations' not in professional_session:
        return jsonify({'error': 'No completed interview'}), 400
    
    results = get_results().get_json()
    
    # Generate HTML report
    report_path = report_generator.save_html_report(results, "Candidate")
    
    return send_file(report_path, as_attachment=True, download_name=f"interview_report_{datetime.now().strftime('%Y%m%d')}.html")

@app.route('/api/token-usage')
def get_token_usage():
    """Get current DeepSeek API token usage"""
    usage = ai_engine.get_token_usage()
    return jsonify({
        'token_usage': usage,
        'api_status': 'enabled' if ai_engine.use_ai else 'disabled',
        'model': ai_engine.model
    })

def generate_final_assessment(avg_score, evaluations):
    """Generate final assessment"""
    if avg_score >= 90:
        return {
            'level': 'EXCEPTIONAL - Senior+ Level',
            'readiness': 'Ready for Staff/Principal roles',
            'timeline': 'Apply immediately',
            'recommended_role': 'Senior Software Architect',
            'confidence': 'Extremely High'
        }
    elif avg_score >= 80:
        return {
            'level': 'STRONG - Senior Level',
            'readiness': 'Ready for Senior roles',
            'timeline': '2-4 weeks prep',
            'recommended_role': 'Senior Software Engineer',
            'confidence': 'High'
        }
    elif avg_score >= 70:
        return {
            'level': 'GOOD - Mid-Senior Level',
            'readiness': 'Ready for Mid-Senior roles',
            'timeline': '6-8 weeks intensive prep',
            'recommended_role': 'Software Engineer',
            'confidence': 'Medium-High'
        }
    elif avg_score >= 60:
        return {
            'level': 'DEVELOPING - Mid Level',
            'readiness': 'Possible Mid level with prep',
            'timeline': '3-6 months preparation',
            'recommended_role': 'Software Engineer',
            'confidence': 'Medium'
        }
    else:
        return {
            'level': 'FOUNDATION BUILDING NEEDED',
            'readiness': 'Not ready for top-tier roles',
            'timeline': '6-12 months intensive development',
            'recommended_role': 'Build fundamentals first',
            'confidence': 'Low'
        }

def calculate_dimension_averages(evaluations):
    """Calculate average dimension scores"""
    dimensions = {}
    
    for eval_data in evaluations:
        eval_scores = eval_data['evaluation']['dimension_scores']
        for dim, score in eval_scores.items():
            if dim not in dimensions:
                dimensions[dim] = []
            dimensions[dim].append(score)
    
    return {dim: sum(scores)/len(scores) for dim, scores in dimensions.items()}

def identify_improvement_areas(evaluations):
    """Identify key improvement areas"""
    all_areas = []
    
    for eval_data in evaluations:
        improvement_roadmap = eval_data['evaluation'].get('improvement_roadmap', [])
        all_areas.extend(improvement_roadmap)
    
    # Count frequency and return top areas
    area_counts = {}
    for area in all_areas:
        area_counts[area] = area_counts.get(area, 0) + 1
    
    return sorted(area_counts.keys(), key=lambda x: area_counts[x], reverse=True)[:5]

def calculate_duration():
    """Calculate interview duration"""
    if 'start_time' in professional_session:
        start = datetime.fromisoformat(professional_session['start_time'])
        duration = (datetime.now() - start).total_seconds() / 60
        return round(duration, 1)
    return 0

if __name__ == '__main__':
    print("Starting Professional Interview Assessment Platform")
    print(f"Server will run on http://localhost:5002")
    print(f" DeepSeek AI Status: {'ENABLED' if ai_engine.use_ai else 'DISABLED'}")
    print(f" Token Usage Endpoint: http://localhost:5002/api/token-usage")
    app.run(debug=True, port=5002)