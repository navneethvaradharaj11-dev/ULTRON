class ConversationModel {
  final String id;
  final String userId;
  final String title;
  final String status;
  final String createdAt;

  ConversationModel({
    required this.id,
    required this.userId,
    required this.title,
    required this.status,
    required this.createdAt,
  });

  factory ConversationModel.fromJson(Map<String, dynamic> json) {
    return ConversationModel(
      id: json['id'] ?? '',
      userId: json['user_id'] ?? '',
      title: json['title'] ?? 'New Conversation',
      status: json['status'] ?? 'active',
      createdAt: json['created_at'] ?? '',
    );
  }
}
