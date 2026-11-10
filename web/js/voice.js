// Web Speech API Voice Controller
class VoiceController {
    constructor() {
        this.synth = window.speechSynthesis;
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = SpeechRecognition ? new SpeechRecognition() : null;
        this.available = Boolean(this.recognition);
        this.listening = false;
        if (this.recognition) {
            this.recognition.lang = navigator.language || 'en-US';
            this.recognition.interimResults = false;
            this.recognition.maxAlternatives = 1;
        }
    }

    speak(text) {
        if (this.synth) {
            const utterance = new SpeechSynthesisUtterance(text);
            this.synth.speak(utterance);
        }
    }

    startListening(onResultCallback, onStateChange = () => {}, onError = () => {}) {
        if (!this.recognition || this.listening) return;

        this.recognition.onresult = (event) => {
            const transcript = event.results[event.resultIndex][0].transcript.trim();
            if (transcript) onResultCallback(transcript);
        };
        this.recognition.onerror = (event) => {
            this.listening = false;
            onStateChange(false);
            onError(event.error);
        };
        this.recognition.onend = () => {
            this.listening = false;
            onStateChange(false);
        };

        try {
            this.recognition.start();
            this.listening = true;
            onStateChange(true);
        } catch (error) {
            this.listening = false;
            onStateChange(false);
            onError(error.message || 'Unable to start voice recognition.');
        }
    }
}

window.voiceController = new VoiceController();
