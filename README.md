# 🎯 AI-Powered Interview Assistant

Advanced interview preparation platform with voice recognition, AI evaluation, and comprehensive feedback.

## ✨ Features

- **🎤 Voice-Only Interface** - Speak your answers naturally
- **🤖 AI-Powered Evaluation** - DeepSeek API integration for intelligent scoring
- **📄 Resume Analysis** - Extract skills and experience from PDF/DOCX
- **📊 Multi-Dimensional Scoring** - 6 key performance dimensions
- **🎯 Personalized Questions** - Role-specific interview questions
- **📈 Detailed Reports** - Comprehensive assessment with improvement suggestions

## 🚀 Quick Start

### Option 1: Easy Setup (Recommended)
1. **Download and run the setup file:**
   ```bash
   # Double-click: setup_and_run.bat
   ```

### Option 2: Manual Setup
1. **Install dependencies:**
   ```bash
   pip install -r requirements_voice.txt
   ```

2. **Set your DeepSeek API key:**
   ```bash
   set DEEPSEEK_API_KEY=your_api_key_here
   ```

3. **Run the application:**
   ```bash
   python minimal_app.py
   ```

4. **Open your browser:**
   ```
   http://localhost:5002
   ```

## 🔧 Configuration

### DeepSeek API Setup
1. Get your API key from [DeepSeek](https://platform.deepseek.com/)
2. Set environment variable: `DEEPSEEK_API_KEY=your_key`
3. Or edit the setup file with your key

### HTTPS for Voice (Optional)
For full voice functionality:
```bash
python generate_cert.py
python start_secure.py
# Visit: https://localhost:5002
```

## 📁 Project Structure

```
├── minimal_app.py              # 🎯 Main application (start here)
├── professional_app_clean.py   # 🔧 Full-featured version
├── mcp_server.py              # 🤖 MCP server for Amazon Q CLI
├── templates/                 # 🎨 Web interface
├── static/                    # 💄 CSS/JS assets
├── enhanced_resume_parser.py  # 📄 Resume processing
├── optimized_deepseek.py      # 🤖 AI integration
└── setup_and_run.bat         # 🚀 One-click setup
```

## 🎮 Usage

1. **Upload Resume** - PDF or DOCX format
2. **Select Role** - Choose your target position
3. **Voice Interview** - Speak your answers (or type)
4. **Get Results** - Detailed evaluation and feedback
5. **Download Report** - Comprehensive assessment PDF

## 🔌 MCP Server Integration

For Amazon Q CLI integration:
```bash
python mcp_server.py
```

Available tools:
- `analyze_resume` - Parse resume files
- `generate_questions` - Create interview questions
- `evaluate_answer` - Score responses

## 🛠️ Troubleshooting

**Voice not working?**
- Use HTTPS: `python start_secure.py`
- Allow microphone permissions in browser

**API errors?**
- Check your DeepSeek API key
- Verify internet connection

**Import errors?**
- Run: `pip install -r requirements_voice.txt`

## 📊 Evaluation Dimensions

1. **Technical Mastery** - Domain expertise
2. **Problem Solving** - Analytical thinking
3. **Communication** - Clarity and articulation
4. **Innovation** - Creative solutions
5. **Leadership** - Team and project management
6. **System Thinking** - Architecture and design

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Submit pull request

## 📄 License

MIT License - See LICENSE file for details

---

**Ready to ace your next interview? Run `setup_and_run.bat` and get started! 🚀**