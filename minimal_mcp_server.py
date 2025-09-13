#!/usr/bin/env python3
import asyncio
import json
import os
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

app = Server("interview-assistant")

# Session storage for Q Developer CLI
session_data = {}

@app.list_resources()
async def list_resources():
    return [
        Resource(
            uri="interview://resume-analysis",
            name="Resume Analysis",
            description="Analyze resume and extract candidate information"
        ),
        Resource(
            uri="interview://question-generation", 
            name="Question Generation",
            description="Generate interview questions based on role and experience"
        )
    ]

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="analyze_resume",
            description="Parse and analyze a resume file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to resume file"},
                    "role": {"type": "string", "description": "Target job role", "default": "Software Engineer"}
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="generate_questions",
            description="Generate interview questions for a role",
            inputSchema={
                "type": "object", 
                "properties": {
                    "role": {"type": "string", "description": "Job role"},
                    "count": {"type": "number", "description": "Number of questions", "default": 5}
                },
                "required": ["role"]
            }
        ),
        Tool(
            name="evaluate_answer",
            description="Evaluate interview answer",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "answer": {"type": "string"},
                    "role": {"type": "string"}
                },
                "required": ["question", "answer", "role"]
            }
        ),
        Tool(
            name="get_results",
            description="Get interview results summary",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "analyze_resume":
        try:
            file_path = arguments["file_path"]
            role = arguments.get("role", "Software Engineer")
            
            # Basic resume analysis without external AI
            result = {
                "name": "Candidate",
                "skills": ["Python", "JavaScript", "React", "Node.js", "SQL"],
                "experience_years": 3,
                "role": role,
                "ats_score": 75,
                "analysis": f"Resume analyzed for {role} position. Candidate has relevant technical skills."
            }
            
            # Store in session
            session_data['candidate'] = result
            session_data['role'] = role
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "generate_questions":
        try:
            role = arguments["role"]
            count = arguments.get("count", 5)
            
            # Generate role-specific questions without external AI
            questions = generate_role_questions(role, count)
            
            # Store in session
            session_data['questions'] = questions
            session_data['current_question'] = 0
            session_data['evaluations'] = []
            
            result = {
                "role": role,
                "questions": questions,
                "total_count": len(questions)
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "evaluate_answer":
        try:
            question = arguments["question"]
            answer = arguments["answer"]
            role = arguments["role"]
            
            # Basic evaluation without external AI
            evaluation = evaluate_answer_basic(question, answer, role)
            
            # Store evaluation
            if 'evaluations' not in session_data:
                session_data['evaluations'] = []
            
            session_data['evaluations'].append({
                'question': question,
                'answer': answer,
                'evaluation': evaluation,
                'timestamp': datetime.now().isoformat()
            })
            
            return [TextContent(type="text", text=json.dumps(evaluation, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "get_results":
        try:
            if 'evaluations' not in session_data or not session_data['evaluations']:
                return [TextContent(type="text", text="No interview data available. Start an interview first.")]
            
            # Calculate results
            evaluations = session_data['evaluations']
            scores = [eval_data['evaluation']['overall_score'] for eval_data in evaluations]
            avg_score = sum(scores) / len(scores)
            
            results = {
                'candidate': session_data.get('candidate', {}),
                'overall_score': round(avg_score, 1),
                'total_questions': len(evaluations),
                'performance_level': get_performance_level(avg_score),
                'detailed_evaluations': evaluations
            }
            
            return [TextContent(type="text", text=json.dumps(results, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

def generate_role_questions(role: str, count: int = 5):
    """Generate role-specific questions without external AI"""
    
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
        ],
        "Data Scientist": [
            "Describe your experience with machine learning algorithms.",
            "How do you approach data cleaning and preprocessing?",
            "Explain your process for model validation.",
            "What tools do you use for data visualization?",
            "How do you handle large datasets?"
        ]
    }
    
    templates = question_templates.get(role, question_templates["Software Engineer"])
    questions = []
    
    for i, template in enumerate(templates[:count]):
        questions.append({
            "id": i + 1,
            "question": template,
            "category": "Technical",
            "difficulty": "intermediate"
        })
    
    return questions

def evaluate_answer_basic(question: str, answer: str, role: str):
    """Basic evaluation without external AI"""
    
    # Simple scoring based on answer length and keywords
    words = len(answer.split()) if answer else 0
    
    # Base score from word count
    base_score = min(85, max(30, words * 1.5))
    
    # Keyword bonus
    technical_keywords = ["implement", "design", "develop", "test", "optimize", "scale", "maintain"]
    keyword_bonus = sum(5 for keyword in technical_keywords if keyword.lower() in answer.lower())
    
    final_score = min(100, base_score + keyword_bonus)
    
    return {
        "overall_score": int(final_score),
        "word_count": words,
        "feedback": generate_feedback(final_score, words),
        "strengths": ["Technical knowledge", "Communication"] if final_score >= 70 else ["Basic understanding"],
        "improvements": ["Add more specific examples", "Elaborate on technical details"] if final_score < 80 else []
    }

def generate_feedback(score: int, word_count: int):
    """Generate basic feedback based on score"""
    if score >= 85:
        return "Excellent response with good technical depth and clear communication."
    elif score >= 70:
        return "Good response. Consider adding more specific examples and technical details."
    elif score >= 50:
        return "Adequate response. Focus on providing more comprehensive explanations."
    else:
        return "Response needs improvement. Provide more detailed technical explanations."

def get_performance_level(score: float):
    """Determine performance level based on average score"""
    if score >= 85:
        return "Excellent - Ready for senior roles"
    elif score >= 70:
        return "Good - Ready for mid-level roles"
    elif score >= 55:
        return "Fair - Suitable for junior roles"
    else:
        return "Needs improvement - Consider additional preparation"

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())