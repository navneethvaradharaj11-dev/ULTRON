# PROJECT ULTRON — PHASE 12.7 REAL ANDROID LAUNCH CHECKLIST

---

## 1. Overview & Verification Policy

This document defines the 17-point physical Android device verification sequence required before granting Public Mobile Beta sign-off. Per Mission 12.7 rules against fabricating physical hardware results, all steps are documented as **PENDING REAL HARDWARE & PUBLIC VPS ALLOCATION**.

---

## 2. Physical Android Device Acceptance Sequence

| Step # | Verification Item | Target Acceptance Standard | Hardware Execution Status |
| :--- | :--- | :--- | :--- |
| **1** | Install Release APK | Build with `flutter build apk --release --dart-define=API_BASE_URL=https://<DOMAIN>/api/v1` installs cleanly | PENDING VPS / HARDWARE |
| **2** | Internet Connectivity | Device connected via cellular network (4G/5G) | PENDING VPS / HARDWARE |
| **3** | User Login | Authenticates via HTTPS API and receives secure JWT token | PENDING VPS / HARDWARE |
| **4** | Send ULTRON Command | Dispatches natural language command ("Analyze dataset") | PENDING VPS / HARDWARE |
| **5** | Streamed WSS Response| Event streaming via `wss://<DOMAIN>/ws/chat/{id}` | PENDING VPS / HARDWARE |
| **6** | Start Workflow | Spawns autonomous multi-step workflow | PENDING VPS / HARDWARE |
| **7** | Observe Workflow | Real-time step progress visualized on Flutter timeline | PENDING VPS / HARDWARE |
| **8** | Pause Workflow | Execution halts immediately on user request | PENDING VPS / HARDWARE |
| **9** | Resume Workflow | Execution resumes from exact checkpoint step | PENDING VPS / HARDWARE |
| **10**| Cancel Workflow | Workflow transitions cleanly to `CANCELLED` state | PENDING VPS / HARDWARE |
| **11**| Approval Request | Autonomy Level 3 triggers interactive approval card | PENDING VPS / HARDWARE |
| **12**| Deny Approval | Action execution blocked cleanly upon user rejection | PENDING VPS / HARDWARE |
| **13**| Knowledge Search | Queries vector knowledge store and renders results | PENDING VPS / HARDWARE |
| **14**| Memory Retrieval | Renders ranked user memory observations | PENDING VPS / HARDWARE |
| **15**| Integration Read | Executes read-only integration query (e.g. GitHub/Email)| PENDING VPS / HARDWARE |
| **16**| Offline Mode | App handles network loss gracefully with retry buffer | PENDING VPS / HARDWARE |
| **17**| Reconnect Session | Network restore automatically re-establishes WSS stream | PENDING VPS / HARDWARE |

---

## 3. Launch Checklist Summary

- **Total Checklist Items**: 17
- **Passed Local Automated Tests**: 8 / 8 Flutter widget & unit tests PASSED.
- **Physical Internet Verification**: Pending Public Cloud VPS and domain allocation.
