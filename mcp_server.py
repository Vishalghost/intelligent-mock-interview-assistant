#!/usr/bin/env python3
import asyncio
import json
import os
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
from enhanced_resume_parser import EnhancedResumeParser
from optimized_deepseek import OptimizedDeepSeekAI
from extreme_questions import ExtremeQuestions
from domain_matcher import DomainMatcher
from live_job_fetcher import LiveJobFetcher

app = Server("interview-assistant")
resume_parser = EnhancedResumeParser()
ai_engine = OptimizedDeepSeekAI()
question_generator = ExtremeQuestions()
domain_matcher = DomainMatcher()
job_fetcher = LiveJobFetcher()

# Session storage for Amazon Q CLI
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
                    "file_path": {"type": "string", "description": "Path to resume file"}
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
                    "experience": {"type": "number", "description": "Years of experience"},
                    "skills": {"type": "array", "items": {"type": "string"}}
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
            name="start_interview",
            description="Start complete interview process",
            inputSchema={
                "type": "object",
                "properties": {
                    "resume_path": {"type": "string"},
                    "role": {"type": "string", "default": "Software Engineer"}
                },
                "required": ["resume_path"]
            }
        ),
        Tool(
            name="get_results",
            description="Get interview results and job matches",
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
            result = resume_parser.parse_resume(arguments["file_path"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "generate_questions":
        try:
            candidate_data = {
                'experience_years': arguments.get('experience', 0),
                'skills': arguments.get('skills', [])
            }
            questions = ai_engine.generate_questions(candidate_data, arguments["role"])
            return [TextContent(type="text", text=json.dumps(questions, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "evaluate_answer":
        try:
            evaluation = ai_engine.evaluate_answer(
                arguments["question"], 
                arguments["answer"], 
                arguments["role"]
            )
            # Store evaluation in session
            if 'evaluations' not in session_data:
                session_data['evaluations'] = []
            session_data['evaluations'].append({
                'question': arguments["question"],
                'answer': arguments["answer"],
                'evaluation': evaluation,
                'timestamp': datetime.now().isoformat()
            })
            return [TextContent(type="text", text=json.dumps(evaluation, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "start_interview":
        try:
            # Parse resume
            resume_data = resume_parser.parse_resume(arguments["resume_path"])
            role = arguments.get("role", "Software Engineer")
            
            # Generate questions
            questions = ai_engine.generate_questions(resume_data, role)
            
            # Determine domain
            domain_analysis = domain_matcher.determine_best_fit_domain(resume_data)
            
            # Store in session
            session_data.update({
                'resume_data': resume_data,
                'questions': questions,
                'role': role,
                'domain_analysis': domain_analysis,
                'evaluations': []
            })
            
            result = {
                'message': f'Interview started for {role} role',
                'candidate': resume_data.get('name', 'Candidate'),
                'questions_count': len(questions),
                'domain': domain_analysis.get('primary_domain'),
                'questions': questions
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "get_results":
        try:
            if 'evaluations' not in session_data or not session_data['evaluations']:
                return [TextContent(type="text", text="No interview data available. Start an interview first.")]
            
            # Calculate overall score
            evaluations = session_data['evaluations']
            scores = [eval_data['evaluation']['overall_score'] for eval_data in evaluations]
            avg_score = sum(scores) / len(scores)
            
            # Get job matches
            resume_data = session_data.get('resume_data', {})
            domain_analysis = session_data.get('domain_analysis', {})
            
            jobs = job_fetcher.fetch_jobs(
                domain=domain_analysis.get('primary_domain', 'Software Development'),
                skills=resume_data.get('skills', [])[:5],
                ats_score=resume_data.get('ats_score', 0)
            )
            
            results = {
                'overall_score': round(avg_score, 1),
                'total_questions': len(evaluations),
                'domain_analysis': domain_analysis,
                'job_matches': jobs[:5],
                'detailed_evaluations': evaluations
            }
            
            return [TextContent(type="text", text=json.dumps(results, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())