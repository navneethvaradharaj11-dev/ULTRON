// Web Speech API Voice Controller
class VoiceController {
    constructor() {
        this.synth = window.speechSynthesis;
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = SpeechRecognition ? new SpeechRecognition() : null;
    }

    speak(text) {
        if (this.synth) {
            const utterance = new SpeechSynthesisUtterance(text);
            this.synth.speak(utterance);
        }
    }

    startListening(onResultCallback) {
        if (this.recognition) {
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                onResultCallback(transcript);
            };
            this.recognition.start();
        } else {
            console.warn("Web Speech Recognition API not supported in this browser.");
        }
    }
}

window.voiceController = new VoiceController();
