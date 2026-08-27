class MessageModel {
  final String id;
  final String senderType;
  final String senderName;
  String content;
  final String createdAt;

  MessageModel({
    required this.id,
    required this.senderType,
    required this.senderName,
    required this.content,
    required this.createdAt,
  });

  factory MessageModel.fromJson(Map<String, dynamic> json) {
    return MessageModel(
      id: json['id'] ?? '',
      senderType: json['sender_type'] ?? 'user',
      senderName: json['sender_name'] ?? 'User',
      content: json['content'] ?? '',
      createdAt: json['created_at'] ?? '',
    );
  }
}
