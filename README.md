# Professional Interview Assessment Platform

Advanced AI-powered interview preparation and evaluation system with comprehensive web interface.

## Features

- **Resume Analysis**: Extract skills, experience, and ATS scores from PDF/DOCX
- **Extreme Questions**: Generate challenging, role-specific interview questions
- **Multi-Dimensional Evaluation**: Advanced AI scoring across 6 key dimensions
- **Professional Web Interface**: Clean, corporate-grade user experience
- **Personalized Resources**: Custom learning paths and preparation roadmaps
- **Job Matching**: Intelligent job recommendations based on performance

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure AWS credentials (optional for enhanced features):
```bash
aws configure
```

3. Start the web application:
```bash
python professional_app.py
```

4. Open your browser to: `http://localhost:5002`

## Alternative Startup

Double-click `run_app.bat` on Windows for easy startup.

## Usage

1. Upload your resume (PDF/DOCX format)
2. Select target position level
3. Complete AI-generated interview questions
4. Review comprehensive evaluation and recommendations
5. Download detailed assessment report

## Core Components

- `professional_app.py` - Flask web application server
- `resume_parser.py` - Advanced resume analysis and parsing
- `extreme_questions.py` - Challenging question generation engine
- `advanced_evaluator.py` - Multi-dimensional response evaluation
- `resources_generator.py` - Personalized learning resource creation
- `job_matcher.py` - Intelligent job opportunity matching

## Web Interface

- **Modern Design**: Professional, clean interface suitable for corporate use
- **Progress Tracking**: Real-time progress indicators throughout assessment
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Interactive Elements**: Dynamic scoring, animations, and feedback

## Assessment Output

- Overall performance score and readiness level
- Dimension-specific analysis (Technical, Communication, Leadership, etc.)
- Personalized improvement recommendations
- Curated learning resources and action plans
- Matching job opportunities with compatibility scores
- Downloadable comprehensive assessment report