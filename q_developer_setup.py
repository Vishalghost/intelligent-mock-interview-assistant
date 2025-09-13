#!/usr/bin/env python3
"""
Q Developer CLI Integration Setup
Configures Q Developer to use our minimal MCP server
"""

import json
import os
from pathlib import Path

class QDeveloperIntegration:
    def __init__(self):
        self.mcp_server_path = Path(__file__).parent / "minimal_mcp_server.py"
        # Q Developer CLI configuration path
        self.config_path = Path.home() / ".aws" / "q" / "mcp_servers.json"
    
    def setup_q_developer_integration(self):
        """Setup Q Developer CLI to use our minimal MCP server"""
        
        # Create Q Developer MCP configuration
        config = {
            "mcpServers": {
                "interview-assistant": {
                    "command": "python",
                    "args": [str(self.mcp_server_path)],
                    "cwd": str(Path(__file__).parent),
                    "description": "AI Interview Assistant - Resume analysis, question generation, and evaluation"
                }
            }
        }
        
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write configuration
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Q Developer MCP configuration created at: {self.config_path}")
        return True
    
    def show_usage_examples(self):
        """Show Q Developer CLI usage examples"""
        
        examples = [
            "# Analyze a resume",
            "@interview-assistant analyze_resume --file_path 'resume.pdf' --role 'Software Engineer'",
            "",
            "# Generate interview questions", 
            "@interview-assistant generate_questions --role 'Frontend Developer' --count 5",
            "",
            "# Evaluate an answer",
            "@interview-assistant evaluate_answer --question 'Describe your JS experience' --answer 'I have 3 years...' --role 'Frontend Developer'",
            "",
            "# Get final results",
            "@interview-assistant get_results"
        ]
        
        print("\nQ Developer CLI Usage Examples:")
        print("=" * 50)
        for example in examples:
            print(example)
        
        return examples

if __name__ == "__main__":
    integration = QDeveloperIntegration()
    integration.setup_q_developer_integration()
    integration.show_usage_examples()