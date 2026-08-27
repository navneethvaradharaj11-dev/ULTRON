class TaskModel {
  final String id;
  final String title;
  final String? description;
  final String status;
  final String priority;
  final String createdAt;

  TaskModel({
    required this.id,
    required this.title,
    this.description,
    required this.status,
    required this.priority,
    required this.createdAt,
  });

  factory TaskModel.fromJson(Map<String, dynamic> json) {
    return TaskModel(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      description: json['description'],
      status: json['status'] ?? 'pending',
      priority: json['priority'] ?? 'medium',
      createdAt: json['created_at'] ?? '',
    );
  }
}
