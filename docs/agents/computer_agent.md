# ComputerAgent Documentation

## Role
`ComputerAgent` is ULTRON's specialist perception-enabled agent responsible for screenshot capture, multi-modal perception state fusion, visual grounding of natural language goals to bounding box targets, and controlled mouse and keyboard interaction.

## Safety Directives
- **Controlled Interaction**: Mouse/keyboard interactions are scoped strictly to viewport coordinates.
- **Fail Closed**: If vision or computer runtime is unavailable, return `VISION_UNAVAILABLE` or `COMPUTER_UNAVAILABLE`.
- **Sensitive Operations**: High-impact actions require backend approval.
- **Confidence Thresholds**: Confidence below 0.60 is strictly rejected (`LOW_CONFIDENCE`).
