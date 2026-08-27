// ULTRON Client WebSocket & API Controller
class UltronClient {
    constructor(serverUrl = 'ws://127.0.0.1:8000') {
        self.serverUrl = serverUrl;
        self.ws = null;
        self.conversationId = 'web_conv_' + Math.random().toString(36).substring(2, 9);
        self.onMessageCallbacks = [];
    }

    connect() {
        const wsUrl = `${self.serverUrl}/ws/chat/${self.conversationId}?user_id=web_user_001`;
        console.log('Connecting ULTRON WebSocket to:', wsUrl);
        self.ws = new WebSocket(wsUrl);

        self.ws.onopen = () => {
            console.log('ULTRON WebSocket Connection Established.');
            document.getElementById('status-badge').innerText = 'CONNECTED';
        };

        self.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            self.onMessageCallbacks.forEach(cb => cb(data));
        };

        self.ws.onclose = () => {
            console.log('ULTRON WebSocket Connection Closed.');
            document.getElementById('status-badge').innerText = 'DISCONNECTED';
        };
    }

    sendMessage(message) {
        if (self.ws && self.ws.readyState === WebSocket.OPEN) {
            self.ws.send(JSON.stringify({ message: message }));
        } else {
            console.error('WebSocket not connected.');
        }
    }

    onMessage(callback) {
        self.onMessageCallbacks.push(callback);
    }
}

window.ultron = new UltronClient();
