class VoiceTranscriber:
    def __init__(self):
        """Initialize browser-based speech recognition"""
        print("Browser Speech Recognition initialized")
    
    def transcribe_audio_data(self, audio_text: str) -> str:
        """Process transcribed text from browser"""
        if audio_text and audio_text.strip():
            return audio_text.strip()
        return ""
    
    @property
    def model(self):
        """Compatibility property"""
        return True