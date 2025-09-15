# 🎯 AI-Powered Voice Interview Assistant

> **Secure interview preparation platform with Hugging Face AI models, voice recognition, and comprehensive evaluation.**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![HuggingFace](https://img.shields.io/badge/AI-HuggingFace-orange.svg)
![Security](https://img.shields.io/badge/Security-Hardened-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎤 **Voice Interface** | Speak your answers naturally with real-time transcription |
| 🤖 **Hugging Face AI** | Advanced NLP models for resume parsing and evaluation |
| 📄 **Smart Resume Analysis** | AI-powered skill extraction and ATS scoring |
| 📊 **Multi-Dimensional Scoring** | 6 key performance dimensions with voice analysis |
| 🎯 **Personalized Questions** | AI-generated role-specific interview questions |
| 📈 **Comprehensive Reports** | Detailed assessment with job recommendations |
| 🌐 **Amazon Q CLI** | Command-line integration with MCP protocol |
| 🔒 **Security Hardened** | CSRF protection, secure file handling, thread safety |

## 🚀 Quick Start

### 🎯 **Secure AI Voice Interview** (Recommended)
```bash
# One-click secure setup:
quick_start.bat
```

### 🛠️ **Manual Setup**
```bash
# 1. Install secure dependencies
pip install -r requirements.txt

# 2. Configure environment (IMPORTANT!)
cp .env.example .env
# Edit .env with your secure configuration

# 3. Start secure voice interview system
python voice_interview_app.py

# 4. Open browser
# https://localhost:5003 (HTTPS recommended)
```

### ⚡ **Amazon Q CLI Integration**
```bash
# CLI interface for batch processing:
python amazon_q_integration.py interview --resume "resume.pdf" --role "Software Engineer"
```

## 🔧 System Architecture

### 🤖 **AI Models Integration**
- **Hugging Face Transformers**: NLP models for skill extraction
- **Speech Recognition**: Real-time voice-to-text conversion
- **Multi-dimensional Evaluation**: 6-factor assessment system
- **Job Matching**: AI-powered role recommendations

### 🔒 **Security Architecture**
- **CSRF Protection**: All forms protected against cross-site attacks
- **File Validation**: Secure upload with type and size validation
- **Thread Safety**: Concurrent session management
- **Environment Config**: Secure credential management
- **Path Security**: Prevention of directory traversal attacks

### 🎤 **Voice Processing Pipeline**
```bash
# Voice input → Speech Recognition → AI Analysis → Evaluation → Report
# All steps include security validation and error handling
```

## 📁 Project Structure

```
📦 intelligent-mock-interview-assistant
├── 🚀 quick_start.bat               # Secure launcher
├── 🎤 voice_interview_app.py        # Main secure voice app
├── 🤖 huggingface_mcp_server.py     # AI processing server
├── 🌐 amazon_q_integration.py       # CLI integration
├── 📄 enhanced_resume_parser.py     # Secure resume processing
├── 📊 report_generator.py           # Secure report generation
├── 📁 templates/                    # HTML templates
│   └── voice_interview.html         # Main interface
├── 📁 static/                       # Static assets
│   ├── app.js                       # Secure JavaScript
│   └── style.css                    # Styling
├── 🔒 .env.example                  # Environment template
├── 📋 requirements.txt              # Secure dependencies
├── 🛡️ SECURITY.md                   # Security documentation
└── 📖 README.md                     # This file
```

## 🎮 How to Use

### 🎤 **Voice Interview Process**

| Step | Action | Description |
|------|--------|-------------|
| 1️⃣ | **Upload Resume** | AI analyzes PDF/DOCX with Hugging Face models |
| 2️⃣ | **AI Question Generation** | Personalized questions based on your skills |
| 3️⃣ | **Voice Answers** | Speak naturally - AI transcribes in real-time |
| 4️⃣ | **AI Evaluation** | Multi-dimensional scoring with voice analysis |
| 5️⃣ | **Comprehensive Report** | Detailed feedback and job recommendations |

### 🌐 **Amazon Q CLI Commands**
```bash
# Analyze resume with AI
python amazon_q_integration.py analyze --resume "resume.pdf" --role "Software Engineer"

# Generate interview questions
python amazon_q_integration.py questions --resume "resume.pdf" --role "Data Scientist"

# Complete voice interview simulation
python amazon_q_integration.py interview --resume "resume.pdf" --role "Frontend Developer"
```

## 🔌 Amazon Q CLI Integration

### 🤖 **MCP Server Features**
- **Resume Analysis**: AI-powered skill extraction
- **Question Generation**: Role-specific interview questions
- **Voice Processing**: Speech-to-text with analysis
- **Evaluation Engine**: Multi-dimensional scoring
- **Report Generation**: Comprehensive assessment

### 🛠️ **Available MCP Tools**
| Tool | Function | Description |
|------|----------|-------------|
| `analyze_resume_hf` | Resume parsing | Hugging Face NLP analysis |
| `generate_questions_hf` | Question creation | AI-generated questions |
| `process_voice_answer` | Voice processing | Speech recognition & analysis |
| `evaluate_answer_hf` | Answer scoring | Multi-dimensional evaluation |
| `complete_interview_hf` | Report generation | Comprehensive assessment |

## 🛠️ Installation & Setup

### 📦 **Secure Dependencies**
```bash
# Install all secure dependencies:
pip install -r requirements.txt

# Key security updates:
# - requests>=2.32.4 (fixes CVE vulnerabilities)
# - Flask-WTF>=1.1.1 (CSRF protection)
# - python-dotenv>=1.0.0 (environment management)
```

### 🔒 **Security Configuration**
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Generate secure keys
python -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('WTF_CSRF_SECRET_KEY=' + secrets.token_hex(32))"

# 3. Edit .env with generated keys and your settings
```

### 🎤 **Voice Setup**
- **Microphone Access**: Browser will request permission
- **HTTPS**: Required for voice features in production
- **Audio Formats**: Supports WAV, MP3, WebM, OGG

## 📊 AI Evaluation System

### 🧠 **Multi-Dimensional Analysis**
| Dimension | Focus Area | AI Analysis |
|-----------|------------|-------------|
| 🔧 **Technical Mastery** | Domain expertise | Keyword analysis, concept depth |
| 🧠 **Problem Solving** | Analytical thinking | Solution approach, methodology |
| 💬 **Communication** | Clarity & articulation | Voice analysis, structure |
| 💡 **Innovation** | Creative solutions | Novel approaches, optimization |
| 👥 **Leadership** | Team management | Collaboration indicators |
| 🏗️ **System Thinking** | Architecture design | Scalability, integration |

### 🎯 **Scoring Algorithm**
- **Weighted Scoring**: Each dimension has specific weight
- **Voice Metrics**: Clarity, confidence, pace analysis
- **Content Analysis**: Technical depth, completeness
- **Hiring Recommendation**: AI-powered decision support

## 🌐 Web Interfaces

### 🎤 **Voice Interview (Port 5003)**
- Real-time voice recording and transcription
- AI-powered question generation
- Multi-dimensional evaluation
- Comprehensive reporting

### 🌐 **Amazon Q CLI**
- Command-line interface for batch processing
- MCP protocol integration
- Automated report generation
- Scriptable workflows

## 🛠️ Troubleshooting

### ❌ **Common Issues**

| Problem | Solution |
|---------|----------|
| 🔒 **CSRF token missing** | Ensure .env has WTF_CSRF_ENABLED=True |
| 📁 **File upload fails** | Check file type (PDF/DOCX) and size (<50MB) |
| 🎤 **Microphone not working** | Use HTTPS, check browser permissions |
| 🤖 **AI models not loading** | Run: `pip install -r requirements.txt` |
| 🔐 **Environment errors** | Copy .env.example to .env and configure |
| 🌐 **MCP server issues** | Check dependencies, restart server |

### 🔧 **Security & Performance**
- **HTTPS Required**: Voice features need secure context
- **Environment Config**: Always use .env for secrets
- **File Validation**: Only PDF/DOCX files accepted
- **Session Security**: Thread-safe concurrent handling
- **GPU Acceleration**: Install CUDA for faster AI processing

## 🚀 Getting Started

### 🎯 **Ready for secure AI-powered interviews?**

1. **Clone this repository**
2. **Run `quick_start.bat`** for secure setup
3. **Configure `.env`** with your secure settings
4. **Start secure interviews**: Access https://localhost:5003
5. **Or use CLI**: `python amazon_q_integration.py interview --resume "your_resume.pdf"`

### 🔒 **Security First**
- ✅ All vulnerabilities fixed (17 → 0)
- ✅ CSRF protection enabled
- ✅ Secure file handling
- ✅ Thread-safe operations
- ✅ Environment-based configuration

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/security-enhancement`)
3. Commit changes (`git commit -m 'Add security feature'`)
4. Push to branch (`git push origin feature/security-enhancement`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

### 🎯 **Ready to ace your next interview with secure AI?**

**Choose your interface:**

[![Secure Voice Interview](https://img.shields.io/badge/Secure%20Voice%20Interview-Start%20Now-brightgreen.svg?style=for-the-badge)](quick_start.bat)
[![Amazon Q CLI](https://img.shields.io/badge/Amazon%20Q%20CLI-Setup-blue.svg?style=for-the-badge)](amazon_q_integration.py)

**Powered by Hugging Face AI Models & Secure Architecture**

</div>