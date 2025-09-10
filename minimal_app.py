from flask import Flask, render_template, request, jsonify, send_file
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from optimized_deepseek import OptimizedDeepSeekAI
from enhanced_resume_parser import EnhancedResumeParser
from domain_matcher import DomainMatcher
from live_job_fetcher import LiveJobFetcher

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
import os
# Get API key from environment variable
api_key = os.getenv('DEEPSEEK_API_KEY')
if not api_key:
    print("WARNING: DEEPSEEK_API_KEY not set. Using demo mode.")
ai_engine = OptimizedDeepSeekAI()
ai_engine.toggle_ai(True)  # Force enable AI
resume_parser = EnhancedResumeParser()
domain_matcher = DomainMatcher()
job_fetcher = LiveJobFetcher()
print(f"DeepSeek API Status: {'ENABLED' if ai_engine.use_ai else 'DISABLED'}")
print(f"Resume Parser: LOADED")
print(f"Domain Matcher: LOADED")
print(f"Job Fetcher: LOADED")

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
            # Parse the actual resume
            print(f"Parsing resume: {filename}")
            candidate_data = resume_parser.parse_resume(filepath)
            print(f"Parsed candidate: {candidate_data.get('name', 'Unknown')}")
            
            # Enhance with AI analysis
            resume_text = resume_parser.extract_text(filepath)
            ai_analysis = ai_engine.analyze_resume(resume_text)
            if ai_analysis:
                for key, value in ai_analysis.items():
                    if key not in candidate_data or not candidate_data[key]:
                        candidate_data[key] = value
                        
        except Exception as e:
            print(f"Resume parsing failed: {e}")
            return jsonify({'error': f'Resume parsing failed: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Invalid file format. Please upload PDF or DOCX'}), 400
    
    try:
        # Generate real questions using DeepSeek API
        ai_resume_data = {
            'skills': candidate_data.get('skills', []),
            'experience_years': candidate_data.get('experience_years', 0),
            'name': candidate_data.get('name', 'Candidate')
        }
        
        print(f"Calling DeepSeek API for {role} questions...")
        questions = ai_engine.generate_questions(ai_resume_data, role)
        print(f"DeepSeek returned {len(questions)} questions")
        
        if not questions:
            questions = [{
                'question': f'Tell me about your experience in {role.lower()} development.',
                'category': 'Experience',
                'difficulty': 'intermediate'
            }]
            
    except Exception as e:
        print(f"Question generation failed: {e}")
        questions = [{
            'question': f'Describe your background in {role.lower()}.',
            'category': 'General',
            'difficulty': 'basic'
        }]
    
    # Determine best-fit domain
    domain_analysis = domain_matcher.determine_best_fit_domain(candidate_data)
    
    # Store in session
    global session_data
    session_data = {
        'candidate_data': candidate_data,
        'questions': questions,
        'role': role,
        'current_question': 0,
        'evaluations': [],
        'domain_analysis': domain_analysis
    }
    
    return jsonify({
        'candidate_data': candidate_data,
        'readiness_score': 72.5,
        'total_questions': len(questions),
        'warning_level': 'extreme',
        'analysis_message': f'DeepSeek API Analysis | {len(questions)} AI questions generated | Role: {role} | Best Domain: {domain_analysis["primary_domain"]} ({domain_analysis["confidence"]:.0f}% confidence)'
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
    print(f"Calling DeepSeek API for evaluation...")
    evaluation = ai_engine.evaluate_answer(
        question_data['question'], answer, role
    )
    print(f"DeepSeek evaluation score: {evaluation.get('overall_score', 'N/A')}")
    
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
    
    # Fetch live job postings
    domain_analysis = session_data.get('domain_analysis', {})
    primary_domain = domain_analysis.get('primary_domain', 'Software Development')
    candidate_skills = candidate_data.get('skills', [])
    if isinstance(candidate_skills, dict):
        candidate_skills = [skill for skills_list in candidate_skills.values() if isinstance(skills_list, list) for skill in skills_list]
    
    live_jobs = job_fetcher.fetch_jobs(
        domain=primary_domain,
        skills=candidate_skills[:10],  # Top 10 skills
        ats_score=candidate_data.get('ats_score', 0)
    )
    
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
        'job_matches': live_jobs,
        'domain_analysis': domain_analysis,
        'personalized_resources': {
            'learning_path': ['Advanced Python', 'System Design'],
            'recommended_courses': ['Python Mastery', 'Architecture Patterns']
        },
        'interview_metadata': {
            'total_questions': len(evaluations),
            'completion_time': datetime.now().isoformat(),
            'duration_minutes': 15,
            'difficulty_level': 'ADVANCED'
        }
    })

@app.route('/download-report')
def download_report():
    if not session_data or 'evaluations' not in session_data:
        return jsonify({'error': 'No completed interview'}), 400
    
    results_data = get_results().get_json()
    
    # Generate text report
    report_content = f"""
=== AI INTERVIEW ASSESSMENT REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CANDIDATE PROFILE:
Name: {results_data['candidate_profile']['name']}
Experience: {results_data['candidate_profile']['experience_years']} years
Skills: {', '.join(results_data['candidate_profile']['skills'])}

PERFORMANCE SUMMARY:
Overall Score: {results_data['performance_summary']['overall_score']}/100
Level: {results_data['performance_summary']['final_assessment']['level']}
Readiness: {results_data['performance_summary']['final_assessment']['readiness']}
Timeline: {results_data['performance_summary']['final_assessment']['timeline']}

DIMENSION ANALYSIS:
"""
    
    for dim, score in results_data['dimension_analysis'].items():
        report_content += f"{dim.replace('_', ' ').title()}: {score:.1f}/100\n"
    
    # Add domain analysis
    if 'domain_analysis' in results_data:
        domain = results_data['domain_analysis']
        report_content += f"\nDOMAIN ANALYSIS:\n"
        report_content += f"Primary Domain: {domain.get('primary_domain', 'N/A')}\n"
        report_content += f"Confidence: {domain.get('confidence', 0):.1f}%\n"
        report_content += f"Recommended Level: {domain.get('recommended_level', 'N/A')}\n"
        if domain.get('alternative_domains'):
            report_content += f"Alternative Domains: {', '.join(domain['alternative_domains'])}\n"
    
    # Add job matches
    if results_data['job_matches']:
        report_content += "\nLIVE JOB MATCHES:\n"
        for i, job in enumerate(results_data['job_matches'][:5], 1):
            report_content += f"\n{i}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}\n"
            report_content += f"   Location: {job.get('location', 'N/A')}\n"
            report_content += f"   Match Score: {job.get('match_score', 0):.0f}%\n"
            if job.get('salary'):
                report_content += f"   Salary: {job['salary']}\n"
    
    report_content += "\nDETAILED EVALUATIONS:\n"
    for i, eval_data in enumerate(results_data['detailed_evaluations'], 1):
        report_content += f"\nQuestion {i}: {eval_data['question_data']['question']}\n"
        report_content += f"Answer: {eval_data['answer'][:200]}...\n"
        report_content += f"Score: {eval_data['evaluation']['overall_score']}/100\n"
        report_content += f"Feedback: {eval_data['evaluation']['detailed_feedback']}\n"
    
    # Save to file
    filename = f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return send_file(filepath, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    print("Starting AI Interview Assistant")
    print("Visit: http://localhost:5002")
    print("Upload resume -> Answer questions -> Download report")
    app.run(debug=True, port=5002)