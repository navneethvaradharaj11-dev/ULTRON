# PROJECT ULTRON — PHASE 12.1 REAL DEVICE & MOBILE CLIENT DEPLOYMENT GUIDE

---

## 1. Flutter Build Configuration for Production

The Flutter mobile application supports dynamic compile-time and runtime API base URL configuration without modifying application source code:

```bash
cd frontend/flutter_app
flutter build apk --release --dart-define=API_BASE_URL=https://api.ultron.ai/api/v1
```

---

## 2. Mobile Network & Connection Hardening

* **HTTP Client Retry**: `ApiService._withRetry` handles transient network drops automatically (up to 2 retries with exponential backoff).
* **WebSocket Service**: `WebSocketService` handles real-time chat event streaming and automatic reconnection.
* **Token Storage**: Secure JWT token persistence via platform-native secure storage (`flutter_secure_storage`).
* **Offline Handling**: Non-blocking offline UI state display when backend API server is unreachable.
