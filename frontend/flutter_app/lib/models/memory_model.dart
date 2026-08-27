class MemoryModel {
  final String id;
  final String content;
  final String memoryType;
  final int importance;
  final String createdAt;

  MemoryModel({
    required this.id,
    required this.content,
    required this.memoryType,
    required this.importance,
    required this.createdAt,
  });

  factory MemoryModel.fromJson(Map<String, dynamic> json) {
    return MemoryModel(
      id: json['id'] ?? '',
      content: json['content'] ?? '',
      memoryType: json['memory_type'] ?? 'long_term',
      importance: json['importance'] ?? 1,
      createdAt: json['created_at'] ?? '',
    );
  }
}
