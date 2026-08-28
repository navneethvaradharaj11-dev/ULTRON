# Phase 5 Architecture: Perception Engine & Controlled Computer Interaction

## Overview
Phase 5 transforms ULTRON into a **Perception-Enabled Agentic AI Operating System**. ULTRON can capture screen viewports, analyze visual UI state, detect visual elements (buttons, text fields, checkboxes, dropdowns, links, tabs, dialogs, tables, cards, icons), ground natural language instructions into visual targets, and execute controlled mouse and keyboard interactions safely within viewport boundaries.

```
USER GOAL
  │
COMMANDER ──► PLANNER ──► TASK GRAPH ──► AGENT ROUTER
                                              │
                                              ▼
                                       COMPUTER AGENT
                                              │
                                              ▼
                                      PERCEPTION ENGINE
                                              │
                       ┌──────────────────────┼──────────────────────┐
                       ▼                      ▼                      ▼
                 Screenshot / OCR       A11y Inspector        Vision Analyzer
                       │                      │                      │
                       └──────────────────────┼──────────────────────┘
                                              ▼
                                   PERCEPTION FUSION ENGINE
                                              │
                                              ▼
                                      VISUAL GROUNDING
                                              │
                                              ▼
                                     COMPUTER POLICY GUARD
                                   (Bounds, Safety, Approval)
                                              │
                                              ▼
                                    CONTROLLED INPUT ENGINE
                                      (Mouse & Keyboard)
                                              │
                                              ▼
                                      VERIFY & RECOVER
```

## Core Components
1. **Perception Engine (`backend/app/perception/perception_engine.py`)**: Multi-modal perception orchestrator.
2. **Vision Analyzer (`backend/app/perception/vision_analyzer.py`)**: Visual region and UI component analysis.
3. **UIDetector (`backend/app/perception/ui_detector.py`)**: Categorizes buttons, text fields, dropdowns, dialogs, cards, icons.
4. **VisualGrounder (`backend/app/perception/visual_grounder.py`)**: Grounds instructions to visual targets with bounding boxes and confidence scores.
5. **OCREngine (`backend/app/perception/ocr_engine.py`)**: Text extraction with untrusted data block wrapping.
6. **AccessibilityTree (`backend/app/perception/accessibility_tree.py`)**: Accessibility tree node parser.
7. **PerceptionFusion (`backend/app/perception/perception_fusion.py`)**: Multi-modal fusion (DOM + A11y + OCR + Vision).
8. **ComputerManager & ActionExecutor (`backend/app/computer/`)**: Controlled mouse/keyboard execution within viewport boundaries.
9. **ComputerSecurityValidator (`backend/app/security/computer_security.py`)**: Enforces bounds, rate limits, sensitive action detection, and approval gates.
