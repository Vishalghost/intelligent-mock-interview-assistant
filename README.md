# 🎯 AI-Powered Interview Assistant

> **Advanced interview preparation platform with voice recognition, AI evaluation, and comprehensive feedback.**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎤 **Voice Interface** | Speak your answers naturally - no typing required |
| 🤖 **AI Evaluation** | DeepSeek API integration for intelligent scoring |
| 📄 **Resume Analysis** | Extract skills and experience from PDF/DOCX files |
| 📊 **Multi-Dimensional Scoring** | 6 key performance dimensions analysis |
| 🎯 **Personalized Questions** | Role-specific interview questions |
| 📈 **Detailed Reports** | Comprehensive assessment with improvement suggestions |

## 🚀 Quick Start

### 🎯 **One-Click Setup** (Recommended)
```bash
# Just double-click this file:
setup_and_run.bat
```

### ⚡ **Instant Demo**
```bash
# Quick test without setup:
quick_start.bat
```

### 🛠️ **Manual Setup**
```bash
# 1. Install dependencies
pip install flask requests PyPDF2 python-docx cryptography

# 2. Set API key
set DEEPSEEK_API_KEY=your_api_key_here

# 3. Run application
python minimal_app.py

# 4. Open browser
# http://localhost:5002
```

## 🔧 Configuration

### 🔑 **DeepSeek API Setup**
1. **Get API Key**: Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. **Set Environment Variable**: 
   ```bash
   set DEEPSEEK_API_KEY=your_api_key_here
   ```
3. **Or use setup file**: `setup_and_run.bat` will prompt for your key

### 🔒 **HTTPS for Voice** (Optional)
```bash
# Generate SSL certificates for voice features
python generate_cert.py
python start_secure.py

# Then visit: https://localhost:5002
```

## 📁 Project Structure

```
📦 intelligent-mock-interview-assistant
├── 🚀 setup_and_run.bat          # One-click installation
├── ⚡ quick_start.bat             # Instant demo
├── 🤖 run_mcp_server.bat         # MCP server for Amazon Q
├── 🎯 minimal_app.py              # Main application
├── 🔧 professional_app_clean.py   # Full-featured version
├── 📄 enhanced_resume_parser.py   # Resume processing
├── 🤖 optimized_deepseek.py       # AI integration
├── 📁 templates/                  # Web interface
└── 📁 static/                     # CSS/JS assets
```

## 🎮 How to Use

| Step | Action | Description |
|------|--------|-------------|
| 1️⃣ | **Upload Resume** | PDF or DOCX format supported |
| 2️⃣ | **Select Role** | Choose your target job position |
| 3️⃣ | **Voice Interview** | Speak your answers naturally |
| 4️⃣ | **Get Results** | Detailed AI evaluation and feedback |
| 5️⃣ | **Download Report** | Comprehensive assessment PDF |

### 🎤 **Voice Features**
- **Browser-based**: No additional software needed
- **Real-time**: Instant speech-to-text conversion
- **HTTPS required**: For security and browser compatibility

## 🔌 Amazon Q CLI Integration

### 🤖 **MCP Server**
```bash
# Start MCP server
run_mcp_server.bat

# Or manually:
python mcp_server.py
```

### 🛠️ **Available Tools**
| Tool | Function | Description |
|------|----------|-------------|
| `analyze_resume` | Resume parsing | Extract skills and experience |
| `generate_questions` | Question creation | Role-specific interview questions |
| `evaluate_answer` | Answer scoring | AI-powered evaluation |

## 🛠️ Troubleshooting

### ❌ **Common Issues**

| Problem | Solution |
|---------|----------|
| 🎤 **Voice not working** | Use HTTPS: `python start_secure.py` <br> Allow microphone permissions |
| 🔑 **API errors** | Check DeepSeek API key <br> Verify internet connection |
| 📦 **Import errors** | Run: `pip install -r requirements_voice.txt` |
| 🌐 **SSL errors** | Delete `cert.pem` and `key.pem`, regenerate |
| 💻 **Encoding issues** | Use `setup_and_run.bat` for automatic handling |

## 📊 AI Evaluation Dimensions

| Dimension | Focus Area | Weight |
|-----------|------------|--------|
| 🔧 **Technical Mastery** | Domain expertise and knowledge | 25% |
| 🧠 **Problem Solving** | Analytical and critical thinking | 20% |
| 💬 **Communication** | Clarity and articulation skills | 20% |
| 💡 **Innovation** | Creative and novel solutions | 15% |
| 👥 **Leadership** | Team and project management | 10% |
| 🏗️ **System Thinking** | Architecture and design approach | 10% |

## 🚀 Getting Started

### 🎯 **Ready to ace your interview?**

1. **Clone this repository**
2. **Double-click `setup_and_run.bat`**
3. **Enter your DeepSeek API key**
4. **Start practicing!**

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

### 🎯 **Ready to ace your next interview?**

**Just run `setup_and_run.bat` and get started!**

[![Get Started](https://img.shields.io/badge/Get%20Started-Now-brightgreen.svg?style=for-the-badge)](setup_and_run.bat)

</div>