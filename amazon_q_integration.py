#!/usr/bin/env python3
"""
Amazon Q CLI Integration for Interview Assistant
Connects the MCP server with Amazon Q CLI
"""

import subprocess
import json
import os
from pathlib import Path

class AmazonQIntegration:
    def __init__(self):
        self.mcp_server_path = Path(__file__).parent / "mcp_server.py"
        self.config_path = Path.home() / ".aws" / "amazonq" / "mcp_config.json"
    
    def setup_amazon_q_integration(self):
        """Setup Amazon Q CLI to use our MCP server"""
        
        # Create Amazon Q MCP configuration
        config = {
            "mcpServers": {
                "interview-assistant": {
                    "command": "python",
                    "args": [str(self.mcp_server_path)],
                    "cwd": str(Path(__file__).parent),
                    "env": {
                        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY", "")
                    }
                }
            }
        }
        
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write configuration
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Amazon Q MCP configuration created at: {self.config_path}")
        return True
    
    def start_interview_via_q(self, resume_path: str, role: str = "Software Engineer"):
        """Start interview through Amazon Q CLI"""
        
        # Amazon Q CLI commands to interact with MCP server
        commands = [
            f"@interview-assistant analyze_resume --file_path {resume_path}",
            f"@interview-assistant generate_questions --role '{role}' --experience 3"
        ]
        
        print("Starting interview via Amazon Q CLI...")
        print("Use these commands in Amazon Q:")
        for cmd in commands:
            print(f"  {cmd}")
        
        return commands

if __name__ == "__main__":
    integration = AmazonQIntegration()
    integration.setup_amazon_q_integration()
    
    # Example usage
    integration.start_interview_via_q("resume.pdf", "Backend Developer")