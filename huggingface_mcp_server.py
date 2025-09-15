#!/usr/bin/env python3
import asyncio
import json
import os
from datetime import datetime, timezone
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import PyPDF2
from docx import Document
import re

app = Server("huggingface-interview-assistant")

# Initialize Hugging Face models
try:
    # Resume parsing and skill extraction
    skill_extractor = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
    text_classifier = pipeline("text-classification", model="microsoft/DialoGPT-medium")
    
    # Voice transcription (if available)
    try:
        speech_recognizer = pipeline("automatic-speech-recognition", model="facebook/wav2vec2-base-960h")
    except:
        speech_recognizer = None
        
    print("✅ Hugging Face models loaded successfully")
except Exception as e:
    print(f"⚠️ Model loading failed: {e}")
    skill_extractor = None
    text_classifier = None
    speech_recognizer = None

# Session storage
session_data = {}

@app.list_resources()
async def list_resources():
    return [
        Resource(
            uri="interview://huggingface-resume-analysis",
            name="HuggingFace Resume Analysis",
            description="AI-powered resume parsing with skill extraction"
        ),
        Resource(
            uri="interview://voice-processing",
            name="Voice Processing",
            description="Speech-to-text and voice analysis"
        )
    ]

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="analyze_resume_hf",
            description="Parse resume using Hugging Face NLP models",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to resume file"},
                    "target_role": {"type": "string", "description": "Target job role", "default": "Software Engineer"}
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="extract_skills_hf",
            description="Extract skills from text using NER models",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to analyze"},
                    "domain": {"type": "string", "description": "Technical domain", "default": "software"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="generate_questions_hf",
            description="Generate role-specific questions with AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {"type": "string", "description": "Job role"},
                    "skills": {"type": "array", "items": {"type": "string"}, "description": "Candidate skills"},
                    "experience_level": {"type": "string", "description": "Experience level", "default": "intermediate"}
                },
                "required": ["role"]
            }
        ),
        Tool(
            name="process_voice_answer",
            description="Process voice input and convert to text",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_file": {"type": "string", "description": "Path to audio file"},
                    "question": {"type": "string", "description": "Interview question"}
                },
                "required": ["audio_file"]
            }
        ),
        Tool(
            name="evaluate_answer_hf",
            description="Evaluate interview answer using AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "answer": {"type": "string"},
                    "role": {"type": "string"},
                    "voice_metrics": {"type": "object", "description": "Voice analysis data"}
                },
                "required": ["question", "answer", "role"]
            }
        ),
        Tool(
            name="complete_interview_hf",
            description="Complete interview and generate comprehensive report",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Interview session ID"}
                },
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "analyze_resume_hf":
        return await analyze_resume_with_hf(arguments)
    elif name == "extract_skills_hf":
        return await extract_skills_with_hf(arguments)
    elif name == "generate_questions_hf":
        return await generate_questions_with_hf(arguments)
    elif name == "process_voice_answer":
        return await process_voice_with_hf(arguments)
    elif name == "evaluate_answer_hf":
        return await evaluate_answer_with_hf(arguments)
    elif name == "complete_interview_hf":
        return await complete_interview_with_hf(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def analyze_resume_with_hf(arguments: dict):
    """Analyze resume using Hugging Face models"""
    try:
        file_path = arguments["file_path"]
        target_role = arguments.get("target_role", "Software Engineer")
        
        # Extract text from resume
        resume_text = extract_text_from_file(file_path)
        
        # Extract candidate information
        candidate_info = extract_candidate_info(resume_text)
        
        # Extract skills using NER
        try:
            skills = await extract_skills_with_hf({"text": resume_text, "domain": "software"})
            skills_data = json.loads(skills[0].text) if skills else {"skills": []}
        except (json.JSONDecodeError, IndexError, KeyError):
            skills_data = {"skills": []}
        
        # Calculate experience and scores
        experience_years = calculate_experience_years(resume_text)
        ats_score = calculate_ats_score(resume_text, target_role)
        
        result = {
            "candidate_info": candidate_info,
            "skills": skills_data.get("skills", []),
            "professional_profile": {
                "experience_years": experience_years,
                "domain_expertise": determine_domain(skills_data.get("skills", [])),
                "seniority_level": determine_seniority(experience_years)
            },
            "assessment_scores": {
                "ats_score": ats_score,
                "technical_depth": calculate_technical_depth(skills_data.get("skills", [])),
                "leadership_potential": calculate_leadership_score(resume_text)
            },
            "target_role": target_role,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in session
        session_data['candidate_analysis'] = result
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Resume analysis error: {str(e)}")]

async def extract_skills_with_hf(arguments: dict):
    """Extract skills using Hugging Face NER models"""
    try:
        text = arguments["text"]
        domain = arguments.get("domain", "software")
        
        if not skill_extractor:
            # Fallback skill extraction
            skills = extract_skills_fallback(text, domain)
        else:
            # Use Hugging Face NER
            entities = skill_extractor(text)
            skills = []
            
            # Technical skills patterns with set for O(1) lookup
            tech_patterns = [
                r'\b(Python|Java|JavaScript|React|Node\.js|Angular|Vue|Django|Flask|Spring|Docker|Kubernetes|AWS|Azure|GCP|SQL|MongoDB|PostgreSQL|Redis|Git|Linux|Windows|MacOS)\b',
                r'\b(HTML|CSS|TypeScript|C\+\+|C#|Ruby|PHP|Go|Rust|Swift|Kotlin|Scala|R|MATLAB|TensorFlow|PyTorch|Pandas|NumPy|Scikit-learn)\b',
                r'\b(Jenkins|Terraform|Ansible|Prometheus|Grafana|Elasticsearch|Kafka|RabbitMQ|Nginx|Apache|Tomcat|JUnit|Pytest|Selenium)\b'
            ]
            
            skills_set = set()
            for pattern in tech_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                skills_set.update(matches)
            
            skills = list(skills_set)
            
            # Add NER entities that look like skills
            for entity in entities:
                if entity['entity'] in ['B-MISC', 'I-MISC'] and len(entity['word']) > 2:
                    word = entity['word'].replace('##', '')
                    if word.isalpha() and word not in skills_set:
                        skills_set.add(word)
            
            skills = list(skills_set)
        
        # Categorize skills
        categorized_skills = categorize_skills(skills)
        
        result = {
            "skills": skills,
            "categorized_skills": categorized_skills,
            "total_skills": len(skills),
            "domain": domain,
            "extraction_method": "huggingface_ner" if skill_extractor else "pattern_matching"
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Skill extraction error: {str(e)}")]

async def generate_questions_with_hf(arguments: dict):
    """Generate interview questions using AI"""
    try:
        role = arguments["role"]
        skills = arguments.get("skills", [])
        experience_level = arguments.get("experience_level", "intermediate")
        
        # Generate role-specific questions
        questions = []
        
        # Technical questions based on skills
        if skills:
            for skill in skills[:3]:  # Top 3 skills
                questions.append({
                    "question": f"Describe your experience with {skill} and how you've used it in real projects.",
                    "category": "Technical",
                    "difficulty": experience_level,
                    "skill_focus": skill,
                    "expected_duration": 3
                })
        
        # Role-specific questions
        role_questions = get_role_specific_questions(role, experience_level)
        questions.extend(role_questions)
        
        # Behavioral questions
        behavioral_questions = get_behavioral_questions(experience_level)
        questions.extend(behavioral_questions[:2])
        
        result = {
            "role": role,
            "questions": questions,
            "total_questions": len(questions),
            "experience_level": experience_level,
            "estimated_duration": sum(q.get("expected_duration", 3) for q in questions)
        }
        
        # Store in session
        session_data['interview_questions'] = result
        session_data['current_question_index'] = 0
        session_data['evaluations'] = []
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Question generation error: {str(e)}")]

async def process_voice_with_hf(arguments: dict):
    """Process voice input using Hugging Face speech recognition"""
    try:
        audio_file = arguments["audio_file"]
        question = arguments.get("question", "")
        
        if not os.path.exists(audio_file):
            return [TextContent(type="text", text=f"Audio file not found: {audio_file}")]
        
        # Voice processing
        if speech_recognizer:
            # Use Hugging Face speech recognition
            transcription = speech_recognizer(audio_file)
            text = transcription.get("text", "")
            confidence = transcription.get("confidence", 0.8)
        else:
            # Fallback - simulate transcription
            text = "Voice input processed successfully. Please provide text version for evaluation."
            confidence = 0.7
        
        # Analyze voice characteristics
        voice_metrics = analyze_voice_characteristics(audio_file)
        
        result = {
            "transcription": {
                "text": text,
                "confidence": confidence,
                "word_count": len(text.split()) if text else 0
            },
            "voice_metrics": voice_metrics,
            "question": question,
            "processing_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Voice processing error: {str(e)}")]

async def evaluate_answer_with_hf(arguments: dict):
    """Evaluate interview answer using AI models"""
    try:
        question = arguments["question"]
        answer = arguments["answer"]
        role = arguments["role"]
        voice_metrics = arguments.get("voice_metrics", {})
        
        # Evaluate answer content
        content_score = evaluate_content_quality(answer, question, role)
        
        # Evaluate communication
        communication_score = evaluate_communication(answer, voice_metrics)
        
        # Technical assessment
        technical_score = evaluate_technical_content(answer, role)
        
        # Overall evaluation
        dimension_scores = {
            "technical_mastery": technical_score,
            "problem_solving": evaluate_problem_solving(answer),
            "communication": communication_score,
            "innovation": evaluate_innovation(answer),
            "leadership": evaluate_leadership(answer),
            "system_thinking": evaluate_system_thinking(answer)
        }
        
        # Calculate weighted overall score
        weights = {
            "technical_mastery": 0.25,
            "problem_solving": 0.20,
            "communication": 0.20,
            "innovation": 0.15,
            "leadership": 0.10,
            "system_thinking": 0.10
        }
        
        overall_score = sum(dimension_scores[dim] * weights[dim] for dim in dimension_scores)
        
        # Generate detailed feedback
        feedback = generate_detailed_feedback(dimension_scores, voice_metrics)
        
        evaluation = {
            "overall_score": int(overall_score),
            "dimension_scores": {k: int(v) for k, v in dimension_scores.items()},
            "detailed_feedback": feedback,
            "voice_analysis": voice_metrics,
            "hiring_recommendation": {
                "decision": "Strong Hire" if overall_score >= 80 else "Hire" if overall_score >= 65 else "No Hire",
                "confidence": min(0.95, max(0.4, overall_score / 100)),
                "reasoning": get_hiring_reasoning(overall_score, dimension_scores)
            },
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store evaluation
        if 'evaluations' not in session_data:
            session_data['evaluations'] = []
        
        session_data['evaluations'].append({
            "question": question,
            "answer": answer,
            "evaluation": evaluation,
            "voice_metrics": voice_metrics
        })
        
        return [TextContent(type="text", text=json.dumps(evaluation, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Answer evaluation error: {str(e)}")]

async def complete_interview_with_hf(arguments: dict):
    """Complete interview and generate comprehensive report"""
    try:
        session_id = arguments.get("session_id", "default")
        
        if 'evaluations' not in session_data or not session_data['evaluations']:
            return [TextContent(type="text", text="No interview data available")]
        
        # Calculate final scores
        evaluations = session_data['evaluations']
        overall_scores = [eval_data['evaluation']['overall_score'] for eval_data in evaluations]
        avg_score = sum(overall_scores) / len(overall_scores)
        
        # Dimension averages
        dimension_averages = {}
        for dim in ['technical_mastery', 'problem_solving', 'communication', 'innovation', 'leadership', 'system_thinking']:
            scores = [eval_data['evaluation']['dimension_scores'][dim] for eval_data in evaluations]
            dimension_averages[dim] = sum(scores) / len(scores)
        
        # Generate final assessment
        final_assessment = generate_final_assessment(avg_score, dimension_averages)
        
        # Job recommendations
        candidate_data = session_data.get('candidate_analysis', {})
        job_recommendations = generate_job_recommendations(candidate_data, avg_score)
        
        # Learning recommendations
        learning_path = generate_learning_recommendations(dimension_averages, candidate_data)
        
        report = {
            "interview_summary": {
                "session_id": session_id,
                "completion_time": datetime.now(timezone.utc).isoformat(),
                "total_questions": len(evaluations),
                "overall_score": round(avg_score, 1),
                "performance_level": final_assessment["level"]
            },
            "candidate_profile": candidate_data,
            "performance_analysis": {
                "overall_score": round(avg_score, 1),
                "dimension_scores": {k: round(v, 1) for k, v in dimension_averages.items()},
                "final_assessment": final_assessment
            },
            "detailed_evaluations": evaluations,
            "job_recommendations": job_recommendations,
            "learning_path": learning_path,
            "next_steps": generate_next_steps(avg_score, dimension_averages)
        }
        
        return [TextContent(type="text", text=json.dumps(report, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Interview completion error: {str(e)}")]

# Helper functions
def extract_text_from_file(file_path: str) -> str:
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

def extract_candidate_info(text: str) -> dict:
    """Extract basic candidate information"""
    # Email extraction
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    # Phone extraction
    phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    
    # Name extraction (simple heuristic)
    lines = text.split('\n')
    name = lines[0].strip() if lines else "Candidate"
    
    return {
        "name": name,
        "email": emails[0] if emails else "",
        "phone": phones[0] if phones else "",
        "location": extract_location(text)
    }

def extract_location(text: str) -> str:
    """Extract location from resume text"""
    location_patterns = [
        r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, State
        r'([A-Z][a-z]+,\s*[A-Z][a-z]+)',  # City, Country
    ]
    
    for pattern in location_patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0]
    
    return ""

def calculate_experience_years(text: str) -> int:
    """Calculate years of experience from resume"""
    # Look for year patterns
    year_pattern = r'\b(19|20)\d{2}\b'
    years = re.findall(year_pattern, text)
    
    if len(years) >= 2:
        years = [int(year) for year in years]
        return max(0, max(years) - min(years))
    
    # Fallback: look for explicit experience mentions
    exp_pattern = r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)'
    matches = re.findall(exp_pattern, text.lower())
    
    if matches:
        return int(matches[0])
    
    return 2  # Default

def calculate_ats_score(text: str, role: str) -> int:
    """Calculate ATS compatibility score"""
    score = 50  # Base score
    
    # Check for common ATS-friendly elements
    if '@' in text:  # Has email
        score += 10
    if re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', text):  # Has phone
        score += 10
    if len(text.split()) > 200:  # Adequate length
        score += 10
    if role.lower() in text.lower():  # Mentions target role
        score += 15
    
    return min(100, score)

def extract_skills_fallback(text: str, domain: str) -> list:
    """Fallback skill extraction using patterns"""
    tech_skills = [
        'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'Angular', 'Vue',
        'Django', 'Flask', 'Spring', 'Docker', 'Kubernetes', 'AWS', 'Azure',
        'GCP', 'SQL', 'MongoDB', 'PostgreSQL', 'Redis', 'Git', 'Linux'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in tech_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills

def categorize_skills(skills: list) -> dict:
    """Categorize skills by type"""
    categories = {
        "programming_languages": [],
        "frameworks": [],
        "databases": [],
        "cloud_platforms": [],
        "tools": []
    }
    
    skill_mapping = {
        "programming_languages": ['Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'PHP', 'Go', 'Rust'],
        "frameworks": ['React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'Express', 'Laravel'],
        "databases": ['SQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch'],
        "cloud_platforms": ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes'],
        "tools": ['Git', 'Jenkins', 'Terraform', 'Ansible', 'Linux', 'Windows']
    }
    
    for skill in skills:
        for category, skill_list in skill_mapping.items():
            if skill in skill_list:
                categories[category].append(skill)
                break
        else:
            categories["tools"].append(skill)
    
    return categories

def determine_domain(skills: list) -> str:
    """Determine primary domain based on skills"""
    domain_keywords = {
        "Frontend Development": ['React', 'Angular', 'Vue', 'HTML', 'CSS', 'JavaScript'],
        "Backend Development": ['Node.js', 'Django', 'Flask', 'Spring', 'API'],
        "Data Science": ['Python', 'R', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy'],
        "DevOps": ['Docker', 'Kubernetes', 'AWS', 'Azure', 'Jenkins', 'Terraform'],
        "Mobile Development": ['React Native', 'Flutter', 'Swift', 'Kotlin', 'Android', 'iOS']
    }
    
    skills_set = set(skills)
    domain_scores = {}
    for domain, keywords in domain_keywords.items():
        score = sum(1 for keyword in keywords if keyword in skills_set)
        domain_scores[domain] = score
    
    return max(domain_scores, key=domain_scores.get) if any(domain_scores.values()) else "Software Development"

def determine_seniority(experience_years: int) -> str:
    """Determine seniority level"""
    if experience_years >= 8:
        return "Senior"
    elif experience_years >= 4:
        return "Mid-level"
    elif experience_years >= 1:
        return "Junior"
    else:
        return "Entry-level"

def calculate_technical_depth(skills: list) -> int:
    """Calculate technical depth score"""
    base_score = min(80, len(skills) * 5)
    
    # Bonus for diverse skill set
    categories = categorize_skills(skills)
    diversity_bonus = len([cat for cat in categories.values() if cat]) * 3
    
    return min(100, base_score + diversity_bonus)

def calculate_leadership_score(text: str) -> int:
    """Calculate leadership potential score"""
    leadership_keywords = ['lead', 'manage', 'team', 'mentor', 'coordinate', 'supervise']
    score = sum(5 for keyword in leadership_keywords if keyword.lower() in text.lower())
    return min(100, max(20, score))

def get_role_specific_questions(role: str, experience_level: str) -> list:
    """Get role-specific interview questions"""
    questions_db = {
        "Software Engineer": [
            {
                "question": "Describe your approach to writing clean, maintainable code.",
                "category": "Technical",
                "difficulty": experience_level,
                "expected_duration": 4
            },
            {
                "question": "How do you handle debugging complex issues in production?",
                "category": "Problem Solving",
                "difficulty": experience_level,
                "expected_duration": 5
            }
        ],
        "Frontend Developer": [
            {
                "question": "Explain your approach to responsive web design and cross-browser compatibility.",
                "category": "Technical",
                "difficulty": experience_level,
                "expected_duration": 4
            }
        ],
        "Backend Developer": [
            {
                "question": "How do you design scalable APIs and handle database optimization?",
                "category": "System Design",
                "difficulty": experience_level,
                "expected_duration": 6
            }
        ]
    }
    
    return questions_db.get(role, questions_db["Software Engineer"])

def get_behavioral_questions(experience_level: str) -> list:
    """Get behavioral interview questions"""
    return [
        {
            "question": "Tell me about a challenging project you worked on and how you overcame obstacles.",
            "category": "Behavioral",
            "difficulty": experience_level,
            "expected_duration": 4
        },
        {
            "question": "Describe a time when you had to work with a difficult team member.",
            "category": "Behavioral",
            "difficulty": experience_level,
            "expected_duration": 3
        }
    ]

def analyze_voice_characteristics(audio_file: str) -> dict:
    """Analyze voice characteristics (placeholder)"""
    return {
        "clarity": 0.8,
        "pace": "moderate",
        "confidence": 0.75,
        "filler_words": 2,
        "duration_seconds": 45
    }

# Constants for scoring
CONTENT_WORD_MULTIPLIER = 1.2
COMMUNICATION_WORD_MULTIPLIER = 1.5
TECH_KEYWORD_BONUS = 3
MIN_CONTENT_SCORE = 20
MAX_SCORE = 100

def evaluate_content_quality(answer: str, question: str, role: str) -> int:
    """Evaluate answer content quality"""
    words = len(answer.split()) if answer else 0
    
    # Base score from length
    base_score = min(80, max(MIN_CONTENT_SCORE, words * CONTENT_WORD_MULTIPLIER))
    
    # Technical keyword bonus
    tech_keywords = ['implement', 'design', 'develop', 'optimize', 'scale', 'maintain']
    answer_lower = answer.lower()
    keyword_bonus = sum(TECH_KEYWORD_BONUS for keyword in tech_keywords if keyword in answer_lower)
    
    return min(MAX_SCORE, base_score + keyword_bonus)

def evaluate_communication(answer: str, voice_metrics: dict) -> int:
    """Evaluate communication quality"""
    words = len(answer.split()) if answer else 0
    base_score = min(90, max(30, words * COMMUNICATION_WORD_MULTIPLIER))
    
    # Voice quality bonus
    if voice_metrics:
        clarity_bonus = int(voice_metrics.get('clarity', 0.5) * 10)
        confidence_bonus = int(voice_metrics.get('confidence', 0.5) * 10)
        base_score += clarity_bonus + confidence_bonus
    
    return min(MAX_SCORE, base_score)

def evaluate_technical_content(answer: str, role: str) -> int:
    """Evaluate technical content"""
    technical_terms = ['algorithm', 'architecture', 'framework', 'database', 'API', 'system', 'performance']
    score = sum(5 for term in technical_terms if term.lower() in answer.lower())
    return min(100, max(30, score + len(answer.split()) * 0.8))

def evaluate_problem_solving(answer: str) -> int:
    """Evaluate problem-solving approach"""
    problem_keywords = ['analyze', 'approach', 'solution', 'strategy', 'method', 'process']
    score = sum(6 for keyword in problem_keywords if keyword.lower() in answer.lower())
    return min(100, max(25, score + len(answer.split()) * 0.9))

def evaluate_innovation(answer: str) -> int:
    """Evaluate innovation and creativity"""
    innovation_keywords = ['creative', 'innovative', 'new', 'improve', 'optimize', 'efficient']
    score = sum(8 for keyword in innovation_keywords if keyword.lower() in answer.lower())
    return min(100, max(15, score + len(answer.split()) * 0.6))

def evaluate_leadership(answer: str) -> int:
    """Evaluate leadership potential"""
    leadership_keywords = ['lead', 'manage', 'team', 'mentor', 'coordinate', 'collaborate']
    score = sum(10 for keyword in leadership_keywords if keyword.lower() in answer.lower())
    return min(100, max(10, score + len(answer.split()) * 0.5))

def evaluate_system_thinking(answer: str) -> int:
    """Evaluate system thinking"""
    system_keywords = ['system', 'architecture', 'design', 'scalable', 'integration', 'component']
    score = sum(7 for keyword in system_keywords if keyword.lower() in answer.lower())
    return min(100, max(20, score + len(answer.split()) * 0.7))

def generate_detailed_feedback(dimension_scores: dict, voice_metrics: dict) -> str:
    """Generate detailed feedback"""
    feedback_parts = []
    
    # Technical feedback
    tech_score = dimension_scores.get('technical_mastery', 0)
    if tech_score >= 80:
        feedback_parts.append("Strong technical knowledge demonstrated.")
    elif tech_score >= 60:
        feedback_parts.append("Good technical understanding, consider adding more specific examples.")
    else:
        feedback_parts.append("Technical knowledge needs improvement. Focus on core concepts.")
    
    # Communication feedback
    comm_score = dimension_scores.get('communication', 0)
    if voice_metrics:
        if voice_metrics.get('clarity', 0) > 0.8:
            feedback_parts.append("Excellent verbal communication clarity.")
        else:
            feedback_parts.append("Consider speaking more clearly and at a moderate pace.")
    
    return " ".join(feedback_parts)

def get_hiring_reasoning(overall_score: int, dimension_scores: dict) -> str:
    """Get hiring decision reasoning"""
    if overall_score >= 80:
        return "Strong performance across all dimensions. Candidate demonstrates excellent technical and communication skills."
    elif overall_score >= 65:
        return "Good overall performance with some areas for improvement. Suitable for the role with proper onboarding."
    else:
        return "Performance below expectations. Candidate needs significant improvement before being ready for this role."

def generate_final_assessment(avg_score: float, dimension_averages: dict) -> dict:
    """Generate final assessment"""
    if avg_score >= 85:
        return {
            "level": "EXCELLENT - Senior Level Ready",
            "readiness": "Ready for senior technical roles",
            "timeline": "Immediate - 2 weeks",
            "confidence": "Very High"
        }
    elif avg_score >= 70:
        return {
            "level": "GOOD - Mid-Senior Level",
            "readiness": "Ready for mid-level roles",
            "timeline": "2-4 weeks preparation",
            "confidence": "High"
        }
    else:
        return {
            "level": "DEVELOPING",
            "readiness": "Needs improvement",
            "timeline": "2-6 months preparation",
            "confidence": "Medium"
        }

def generate_job_recommendations(candidate_data: dict, avg_score: float) -> list:
    """Generate job recommendations"""
    skills = candidate_data.get('skills', [])
    experience = candidate_data.get('professional_profile', {}).get('experience_years', 0)
    
    recommendations = []
    
    if 'React' in skills or 'Angular' in skills:
        recommendations.append({
            "title": "Frontend Developer",
            "match_score": min(95, avg_score + 10),
            "reasoning": "Strong frontend skills alignment"
        })
    
    if 'Python' in skills or 'Java' in skills:
        recommendations.append({
            "title": "Backend Developer",
            "match_score": min(95, avg_score + 5),
            "reasoning": "Backend development skills present"
        })
    
    return recommendations

def generate_learning_recommendations(dimension_averages: dict, candidate_data: dict) -> dict:
    """Generate learning path recommendations"""
    weak_areas = [dim for dim, score in dimension_averages.items() if score < 70]
    
    recommendations = {
        "priority_areas": weak_areas,
        "suggested_courses": [],
        "practice_projects": [],
        "timeline": "3-6 months"
    }
    
    if 'technical_mastery' in weak_areas:
        recommendations["suggested_courses"].append("Advanced Technical Skills Bootcamp")
    
    if 'communication' in weak_areas:
        recommendations["suggested_courses"].append("Technical Communication Workshop")
    
    return recommendations

def generate_next_steps(avg_score: float, dimension_averages: dict) -> list:
    """Generate next steps"""
    steps = []
    
    if avg_score >= 80:
        steps.append("Apply for senior-level positions")
        steps.append("Prepare for system design interviews")
    elif avg_score >= 65:
        steps.append("Apply for mid-level positions")
        steps.append("Practice coding interviews")
    else:
        steps.append("Focus on fundamental skill building")
        steps.append("Complete relevant online courses")
    
    return steps

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())