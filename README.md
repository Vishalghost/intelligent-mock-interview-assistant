# 🎯 AI-Powered Voice Interview Assistant

> **Complete interview preparation platform with real job matching, AI analysis, and voice evaluation.**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![AWS](https://img.shields.io/badge/AWS-Amazon%20Q-orange.svg)
![Jobs](https://img.shields.io/badge/Jobs-Real%20API-green.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎤 **Voice Interface** | Real-time speech recognition and voice analysis |
| 🤖 **Amazon Q Integration** | AWS-powered AI for dynamic question generation |
| 💼 **Real Job Matching** | Live job postings from Adzuna API with salary data |
| 📄 **Smart Resume Analysis** | AI skill extraction and professional profiling |
| 📊 **Multi-Dimensional Scoring** | 6-factor performance evaluation system |
| 🎯 **Personalized Questions** | Skill-based dynamic interview questions |
| 📈 **Live Job Recommendations** | Real opportunities with direct apply links |
| 🔒 **Enterprise Security** | CSRF protection and secure data handling |

## 🚀 Quick Start

### 🚀 **Quick Start with Real Jobs**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure APIs
cp .env.example .env
# Add your Adzuna API credentials to .env

# 3. Start voice interview system
python amazon_q_voice_app.py

# 4. Access interface
# http://localhost:5003
```

### 💼 **Test Real Job Integration**
```bash
# Test job API with your skills:
python test_job_api.py

# CLI question generation:
python aws_q_working.py questions --resume "resume.pdf" --role "Software Engineer"
```

## 🔧 System Architecture

### 🤖 **AI & Job Integration**
- **Amazon Q Developer**: AWS-powered question generation
- **Adzuna Job API**: Live job postings from 1000+ sources
- **Speech Recognition**: Real-time voice transcription
- **Smart Matching**: Skills-based job ranking with salary data

### 🔒 **Security Architecture**
- **CSRF Protection**: All forms protected against cross-site attacks
- **File Validation**: Secure upload with type and size validation
- **Thread Safety**: Concurrent session management
- **Environment Config**: Secure credential management
- **Path Security**: Prevention of directory traversal attacks

### 💼 **Complete Interview Pipeline**
```bash
# Resume Upload → AI Analysis → Voice Interview → Real Job Matching → Report
# Integrated with live job APIs and AWS services
```

## 📁 Project Structure

```
📦 intelligent-mock-interview-assistant
├── 🎤 amazon_q_voice_app.py         # Main voice interview app
├── 💼 job_api_integration.py        # Real job API integration
├── 🤖 aws_q_working.py              # Amazon Q Developer integration
├── 📊 test_job_api.py               # Job API testing
├── 🧪 test_voice_app.py             # Complete system testing
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
| 1️⃣ | **Upload Resume** | AI extracts skills and analyzes experience |
| 2️⃣ | **Dynamic Questions** | Amazon Q generates personalized questions |
| 3️⃣ | **Voice Interview** | Real-time speech recognition and analysis |
| 4️⃣ | **Performance Scoring** | Multi-dimensional evaluation system |
| 5️⃣ | **Real Job Matching** | Live job postings with salary data and apply links |

### 💼 **Real Job API Commands**
```bash
# Test job integration
python test_job_api.py

# Generate questions with AWS
python aws_q_working.py questions --resume "resume.pdf" --role "Software Engineer"

# Complete voice interview with real jobs
python amazon_q_voice_app.py
```

## 🔌 Amazon Q CLI Integration

### 💼 **Real Job Integration Features**
- **Live Job Fetching**: Current openings from Adzuna API
- **Skill Matching**: Jobs ranked by resume skills
- **Salary Insights**: Real market data and ranges
- **Direct Applications**: One-click apply to positions
- **Multiple Sources**: Expandable to more job APIs

### 🛠️ **Available Job APIs**
| API | Coverage | Features |
|-----|----------|----------|
| **Adzuna** | 1000+ job boards | Free tier, global coverage |
| **JSearch** | LinkedIn, Indeed, Glassdoor | Premium features via RapidAPI |
| **GitHub Jobs** | Tech-focused | Developer positions (discontinued) |
| **Custom APIs** | Expandable | Add your preferred job sources |

## 🛠️ Installation & Setup

### 📦 **Dependencies & APIs**
```bash
# Install dependencies:
pip install -r requirements.txt

# Key packages:
# - flask (web framework)
# - boto3 (AWS integration)
# - requests (API calls)
# - python-dotenv (environment management)
```

### 🔑 **API Configuration**
```bash
# 1. Get Adzuna API credentials (free):
# https://developer.adzuna.com/

# 2. Add to .env file:
ADZUNA_APP_ID=your_app_id
ADZUNA_API_KEY=your_api_key

# 3. Optional: Add RapidAPI key for more sources
RAPIDAPI_KEY=your_rapidapi_key
```

### 🎤 **Voice Setup**
- **Microphone Access**: Browser will request permission
- **HTTPS**: Required for voice features in production
- **Audio Formats**: Supports WAV, MP3, WebM, OGG

## 📊 AI Evaluation System

### 💼 **Real Job Matching System**
| Feature | Description | Benefit |
|---------|-------------|----------|
| 🎯 **Skill Matching** | Jobs ranked by resume skills | Relevant opportunities |
| 💰 **Salary Data** | Real market rates | Informed negotiations |
| 📍 **Location Filter** | Geographic preferences | Targeted search |
| 🏢 **Company Insights** | Employer information | Better decisions |
| 🔗 **Direct Apply** | One-click applications | Faster process |
| 📊 **Market Trends** | Industry insights | Career planning |

### 🎯 **Job Ranking Algorithm**
- **Skill Match Score**: Percentage of skills alignment
- **Salary Range**: Market-competitive compensation
- **Company Rating**: Employer reputation boost
- **Location Preference**: Geographic relevance
- **Experience Level**: Seniority appropriateness

## 🌐 Web Interfaces

### 🎤 **Voice Interview System**
- Real-time speech recognition
- Dynamic question generation via Amazon Q
- Multi-dimensional performance scoring
- Live job matching with salary data

### 💼 **Job Integration Dashboard**
- Real job postings from Adzuna API
- Skill-based job recommendations
- Salary insights and market data
- Direct application links

## 🛠️ Troubleshooting

### ❌ **Common Issues**

| Problem | Solution |
|---------|----------|
| 💼 **No jobs found** | Check Adzuna API credentials in .env |
| 📁 **File upload fails** | Verify PDF/DOCX format and size (<50MB) |
| 🎤 **Voice not working** | Enable microphone permissions in browser |
| 🤖 **Questions undefined** | Restart app: `python amazon_q_voice_app.py` |
| 🔐 **API errors** | Verify .env configuration and API quotas |
| 🌐 **Connection issues** | Check internet and API service status |

### 🔧 **Performance & APIs**
- **API Rate Limits**: Adzuna free tier: 1000 calls/month
- **Caching**: Job results cached for optimal performance
- **Error Handling**: Graceful fallbacks if APIs unavailable
- **Multi-Source**: Expandable to additional job APIs
- **Real-Time**: Live job data with current salary information

## 🚀 Getting Started

### 🚀 **Ready for AI interviews with real job matching?**

1. **Clone this repository**
2. **Get Adzuna API credentials** (free at developer.adzuna.com)
3. **Configure `.env`** with your API keys
4. **Start interviews**: `python amazon_q_voice_app.py`
5. **Access**: http://localhost:5003

### 💼 **Real Job Integration**
- ✅ Live job postings from Adzuna API
- ✅ Skill-based job matching
- ✅ Real salary data and insights
- ✅ Direct application links
- ✅ Market trend analysis

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

**Choose your path:**

[![Voice Interview](https://img.shields.io/badge/Voice%20Interview-Start%20Now-brightgreen.svg?style=for-the-badge)](amazon_q_voice_app.py)
[![Test Jobs API](https://img.shields.io/badge/Test%20Jobs%20API-Verify%20Setup-blue.svg?style=for-the-badge)](test_job_api.py)

**Powered by Amazon Q Developer & Real Job APIs**

</div>