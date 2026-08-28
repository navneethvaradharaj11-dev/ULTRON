class PerceptionElement {
  final String id;
  final String type;
  final String label;
  final Map<String, dynamic> bbox;
  final double confidence;
  final bool interactive;
  final bool sensitive;

  PerceptionElement({
    required this.id,
    required this.type,
    required this.label,
    required this.bbox,
    required this.confidence,
    this.interactive = true,
    this.sensitive = false,
  });

  factory PerceptionElement.fromJson(Map<String, dynamic> json) {
    return PerceptionElement(
      id: json['id'] ?? json['element_id'] ?? '',
      type: json['type'] ?? 'element',
      label: json['label'] ?? json['description'] ?? '',
      bbox: Map<String, dynamic>.from(json['bbox'] ?? {}),
      confidence: (json['confidence'] as num?)?.toDouble() ?? 1.0,
      interactive: json['interactive'] ?? true,
      sensitive: json['sensitive'] ?? false,
    );
  }
}

class ComputerActionItem {
  final String actionId;
  final String sessionId;
  final String actionType;
  final String status;
  final String approvalState;
  final double confidence;
  final String timestamp;

  ComputerActionItem({
    required this.actionId,
    required this.sessionId,
    required this.actionType,
    required this.status,
    required this.approvalState,
    required this.confidence,
    required this.timestamp,
  });

  factory ComputerActionItem.fromJson(Map<String, dynamic> json) {
    return ComputerActionItem(
      actionId: json['action_id'] ?? '',
      sessionId: json['session_id'] ?? '',
      actionType: json['action_type'] ?? 'UNKNOWN',
      status: json['status'] ?? 'PENDING',
      approvalState: json['approval_state'] ?? 'AUTO_APPROVED',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 1.0,
      timestamp: json['timestamp'] ?? '',
    );
  }
}
