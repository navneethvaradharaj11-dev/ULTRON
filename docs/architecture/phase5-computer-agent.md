# Phase 5 Architecture: ComputerAgent Specialist

## Overview
`ComputerAgent` is ULTRON's specialist perception-enabled agent. It operates through the `OBSERVE` → `PERCEIVE` → `GROUND` → `ACT` → `VERIFY` → `RECOVER` execution loop.

## Agent Loop
1. **OBSERVE & PERCEIVE**: Captures screen viewports, analyzes UI components, and fuses multi-modal perception sources.
2. **GROUND TARGET**: Converts natural language instructions into visual targets with bounding boxes and confidence scores.
3. **SAFETY CHECK & ACT**: Validates action safety against `ComputerSecurityValidator` and dispatches controlled mouse/keyboard inputs.
4. **VERIFY**: Confirms completion status or triggers backend approval when sensitive operations are detected.
5. **RECOVER**: Performs recovery actions if initial targets fail or confidence drops below thresholds.
