class AutonomyRuleModel {
  final String ruleId;
  final String name;
  final String? description;
  final bool enabled;
  final String triggerType;
  final String priority;
  final String autonomyLevel;
  final String createdAt;

  AutonomyRuleModel({
    required this.ruleId,
    required this.name,
    this.description,
    required this.enabled,
    required this.triggerType,
    required this.priority,
    required this.autonomyLevel,
    required this.createdAt,
  });

  factory AutonomyRuleModel.fromJson(Map<String, dynamic> json) {
    return AutonomyRuleModel(
      ruleId: json['rule_id'] ?? json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'],
      enabled: json['enabled'] ?? true,
      triggerType: json['trigger_type'] ?? 'SCHEDULE',
      priority: json['priority'] ?? 'MEDIUM',
      autonomyLevel: json['autonomy_level'] ?? 'LEVEL_1',
      createdAt: json['created_at'] ?? '',
    );
  }
}

class AutonomyNotificationModel {
  final String notificationId;
  final String title;
  final String summary;
  final String priority;
  final bool isRead;
  final String createdAt;

  AutonomyNotificationModel({
    required this.notificationId,
    required this.title,
    required this.summary,
    required this.priority,
    required this.isRead,
    required this.createdAt,
  });

  factory AutonomyNotificationModel.fromJson(Map<String, dynamic> json) {
    return AutonomyNotificationModel(
      notificationId: json['notification_id'] ?? json['id'] ?? '',
      title: json['title'] ?? '',
      summary: json['summary'] ?? '',
      priority: json['priority'] ?? 'MEDIUM',
      isRead: json['is_read'] ?? false,
      createdAt: json['created_at'] ?? '',
    );
  }
}
