#!/usr/bin/env python3
import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
from enhanced_resume_parser import EnhancedResumeParser
from optimized_deepseek import OptimizedDeepSeekAI
from extreme_questions import ExtremeQuestions

app = Server("interview-assistant")
resume_parser = EnhancedResumeParser()
ai_engine = OptimizedDeepSeekAI()
question_generator = ExtremeQuestions()

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
            return [TextContent(type="text", text=json.dumps(evaluation, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())