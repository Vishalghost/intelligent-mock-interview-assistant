// Enhanced JavaScript functionality for better UX

class InterviewAssistant {
    constructor() {
        this.currentSession = {};
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkBrowserSupport();
    }

    setupEventListeners() {
        // File upload validation
        document.getElementById('resume').addEventListener('change', this.validateFile);
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                const submitBtn = document.querySelector('#interview-section .btn-success');
                if (submitBtn && !submitBtn.disabled) {
                    this.submitAnswer();
                }
            }
        });

        // Auto-save answers
        const answerField = document.getElementById('answer');
        if (answerField) {
            answerField.addEventListener('input', this.autoSave);
        }
    }

    validateFile(event) {
        const file = event.target.files[0];
        if (!file) return;

        const maxSize = 10 * 1024 * 1024; // 10MB
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];

        if (file.size > maxSize) {
            this.showAlert('File size must be less than 10MB', 'error');
            event.target.value = '';
            return;
        }

        if (!allowedTypes.includes(file.type)) {
            this.showAlert('Please upload a PDF or DOCX file', 'error');
            event.target.value = '';
            return;
        }

        this.showAlert('File validated successfully!', 'success');
    }

    autoSave() {
        const answer = document.getElementById('answer').value;
        localStorage.setItem('currentAnswer', answer);
    }

    restoreAnswer() {
        const saved = localStorage.getItem('currentAnswer');
        if (saved) {
            document.getElementById('answer').value = saved;
        }
    }

    checkBrowserSupport() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            console.warn('Voice recording not supported in this browser');
            const voiceBtn = document.getElementById('voice-btn');
            if (voiceBtn) {
                voiceBtn.style.display = 'none';
            }
        }
    }

    async startAdvancedVoiceRecording() {
        if (!this.isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        sampleRate: 44100
                    }
                });
                
                this.mediaRecorder = new MediaRecorder(stream, {
                    mimeType: 'audio/webm;codecs=opus'
                });
                
                this.audioChunks = [];
                
                this.mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        this.audioChunks.push(event.data);
                    }
                };
                
                this.mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                    await this.processAudioBlob(audioBlob);
                    stream.getTracks().forEach(track => track.stop());
                };
                
                this.mediaRecorder.start(1000); // Collect data every second
                this.isRecording = true;
                this.updateVoiceButton(true);
                this.startRecordingTimer();
                
            } catch (error) {
                this.showAlert('Microphone access denied or not available', 'error');
            }
        } else {
            this.stopRecording();
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.updateVoiceButton(false);
            this.stopRecordingTimer();
        }
    }

    updateVoiceButton(recording) {
        const btn = document.getElementById('voice-btn');
        if (recording) {
            btn.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
            btn.classList.add('btn-danger');
        } else {
            btn.innerHTML = '<i class="fas fa-microphone"></i> Record Voice Answer';
            btn.classList.remove('btn-danger');
        }
    }

    startRecordingTimer() {
        let seconds = 0;
        this.recordingTimer = setInterval(() => {
            seconds++;
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            const timeStr = `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
            document.getElementById('voice-btn').innerHTML = 
                `<i class="fas fa-stop"></i> Recording... ${timeStr}`;
        }, 1000);
    }

    stopRecordingTimer() {
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = null;
        }
    }

    async processAudioBlob(audioBlob) {
        // For now, just indicate that audio was recorded
        // In a full implementation, you'd send this to a speech-to-text service
        const currentAnswer = document.getElementById('answer').value;
        const audioText = '[Voice recording completed - processing with speech-to-text...]';
        document.getElementById('answer').value = currentAnswer + '\n\n' + audioText;
        
        this.showAlert('Voice recording completed! You can edit the text or submit as is.', 'success');
    }

    showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'check-circle'}"></i> 
            ${message}
            <button onclick="this.parentElement.remove()" style="float: right; background: none; border: none; font-size: 18px; cursor: pointer;">&times;</button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentElement) {
                alertDiv.remove();
            }
        }, 5000);
    }

    async submitAnswer() {
        const answer = document.getElementById('answer').value.trim();
        if (!answer) {
            this.showAlert('Please provide an answer before submitting', 'error');
            return;
        }
        
        // Clear auto-saved answer
        localStorage.removeItem('currentAnswer');
        
        this.showLoading('AI is evaluating your response...');
        
        try {
            const response = await fetch('/answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ answer })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            this.hideLoading();
            this.showEvaluation(data.evaluation);
            
            setTimeout(() => {
                if (data.next_question) {
                    this.loadNextQuestion();
                } else {
                    this.showResults();
                }
            }, 4000);
            
        } catch (error) {
            this.hideLoading();
            this.showAlert('Failed to submit answer: ' + error.message, 'error');
        }
    }

    showEvaluation(evaluation) {
        const evalDiv = document.createElement('div');
        evalDiv.className = 'evaluation-card';
        evalDiv.style.animation = 'slideIn 0.5s ease-out';
        
        evalDiv.innerHTML = `
            <h4><i class="fas fa-chart-bar"></i> Evaluation Results</h4>
            <div class="score-display ${evaluation.score >= 80 ? 'score-excellent' : evaluation.score >= 60 ? 'score-good' : 'score-poor'}">
                ${evaluation.score}/100
            </div>
            <p><strong><i class="fas fa-comment"></i> Feedback:</strong> ${evaluation.feedback}</p>
            ${evaluation.strengths ? `<p><strong><i class="fas fa-thumbs-up"></i> Strengths:</strong> ${Array.isArray(evaluation.strengths) ? evaluation.strengths.join(', ') : evaluation.strengths}</p>` : ''}
            ${evaluation.improvements ? `<p><strong><i class="fas fa-lightbulb"></i> Improvements:</strong> ${Array.isArray(evaluation.improvements) ? evaluation.improvements.join(', ') : evaluation.improvements}</p>` : ''}
        `;
        
        document.getElementById('interview-section').appendChild(evalDiv);
        
        // Add slide-in animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        setTimeout(() => {
            evalDiv.remove();
            style.remove();
        }, 4000);
    }

    showLoading(message) {
        const loadingSection = document.getElementById('loading-section');
        loadingSection.classList.remove('hidden');
        loadingSection.querySelector('h3').textContent = message;
    }

    hideLoading() {
        document.getElementById('loading-section').classList.add('hidden');
    }

    async loadNextQuestion() {
        try {
            const response = await fetch('/question');
            const data = await response.json();
            
            if (data.completed) {
                await this.showResults();
                return;
            }
            
            const progress = (data.question_number / data.total_questions) * 100;
            document.getElementById('question-progress').style.width = progress + '%';
            
            document.getElementById('question-container').innerHTML = `
                <h3><i class="fas fa-question"></i> Question ${data.question_number} of ${data.total_questions}</h3>
                <p style="font-size: 1.1em; line-height: 1.6;">${data.question}</p>
            `;
            
            document.getElementById('answer').value = '';
            this.restoreAnswer(); // Restore any auto-saved content
            
        } catch (error) {
            this.showAlert('Failed to load question: ' + error.message, 'error');
        }
    }

    async showResults() {
        this.showLoading('Generating your final report...');
        
        try {
            const response = await fetch('/results');
            const data = await response.json();
            
            this.hideLoading();
            
            document.getElementById('interview-section').classList.add('hidden');
            document.getElementById('results-section').classList.remove('hidden');
            
            this.displayResults(data);
            
        } catch (error) {
            this.hideLoading();
            this.showAlert('Failed to load results: ' + error.message, 'error');
        }
    }

    displayResults(data) {
        const avgScore = data.average_score.toFixed(1);
        const scoreClass = avgScore >= 80 ? 'score-excellent' : avgScore >= 60 ? 'score-good' : 'score-poor';
        
        const jobsHtml = data.job_matches && data.job_matches.length > 0 ? 
            data.job_matches.map(job => `
                <li class="job-item">
                    <strong>${job.title || job.position || 'Position Available'}</strong><br>
                    <span style="color: #666;">${job.company || 'Company'}</span>
                    ${job.match_score ? `<span style="float: right; color: #4CAF50;">${job.match_score.toFixed(0)}% match</span>` : ''}
                </li>
            `).join('') : '<li class="job-item">No matching jobs found at this time</li>';
        
        document.getElementById('results-data').innerHTML = `
            <div class="score-display ${scoreClass}">
                <i class="fas fa-trophy"></i> Overall Score: ${avgScore}/100
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${data.evaluations.length}</div>
                    <div>Questions Answered</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value ${scoreClass}">${avgScore}</div>
                    <div>Average Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${data.job_matches ? data.job_matches.length : 0}</div>
                    <div>Job Matches</div>
                </div>
            </div>
            
            <div class="card" style="margin: 20px 0;">
                <h3><i class="fas fa-bullseye"></i> Recommended Domain</h3>
                <p style="font-size: 1.2em; color: #2196F3; font-weight: bold;">${data.recommended_domain}</p>
            </div>
            
            <div class="card">
                <h3><i class="fas fa-briefcase"></i> Job Recommendations</h3>
                <ul class="job-list">${jobsHtml}</ul>
            </div>
        `;
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.interviewApp = new InterviewAssistant();
});

// Global functions for HTML onclick events
function startVoiceRecording() {
    window.interviewApp.startAdvancedVoiceRecording();
}

function submitAnswer() {
    window.interviewApp.submitAnswer();
}

function downloadResults() {
    const results = {
        timestamp: new Date().toISOString(),
        session: window.interviewApp.currentSession
    };
    
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `interview_results_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
}