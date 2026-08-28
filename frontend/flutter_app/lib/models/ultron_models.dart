class UltronSystemStatusModel {
  final String operatingSystem;
  final String systemStatus;
  final int totalCapabilities;
  final int availableCapabilities;

  UltronSystemStatusModel({
    required this.operatingSystem,
    required this.systemStatus,
    required this.totalCapabilities,
    required this.availableCapabilities,
  });

  factory UltronSystemStatusModel.fromJson(Map<String, dynamic> json) {
    return UltronSystemStatusModel(
      operatingSystem: json['operating_system'] ?? 'ULTRON OS v10.0.0',
      systemStatus: json['system_status'] ?? 'HEALTHY',
      totalCapabilities: json['total_capabilities'] ?? 11,
      availableCapabilities: json['available_capabilities'] ?? 11,
    );
  }
}

class UltronActivityModel {
  final String activityId;
  final String? workflowId;
  final String activityType;
  final String title;
  final String? details;
  final String createdAt;

  UltronActivityModel({
    required this.activityId,
    this.workflowId,
    required this.activityType,
    required this.title,
    this.details,
    required this.createdAt,
  });

  factory UltronActivityModel.fromJson(Map<String, dynamic> json) {
    return UltronActivityModel(
      activityId: json['activity_id'] ?? json['id'] ?? '',
      workflowId: json['workflow_id'],
      activityType: json['activity_type'] ?? 'ACTIVITY',
      title: json['title'] ?? '',
      details: json['details'],
      createdAt: json['created_at'] ?? '',
    );
  }
}
