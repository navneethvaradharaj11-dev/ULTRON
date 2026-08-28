class MemoryModel {
  final String id;
  final String userId;
  final String type;
  final String content;
  final int importance;
  final double confidence;
  final String source;
  final String createdAt;
  final String updatedAt;
  final String lastAccessed;
  final int accessCount;
  final String status;
  final double score;

  MemoryModel({
    required this.id,
    required this.userId,
    required this.type,
    required this.content,
    required this.importance,
    required this.confidence,
    required this.source,
    required this.createdAt,
    required this.updatedAt,
    required this.lastAccessed,
    required this.accessCount,
    required this.status,
    this.score = 1.0,
  });

  factory MemoryModel.fromJson(Map<String, dynamic> json) {
    return MemoryModel(
      id: json['id'] ?? '',
      userId: json['user_id'] ?? '',
      type: json['type'] ?? json['memory_type'] ?? 'SEMANTIC',
      content: json['content'] ?? '',
      importance: json['importance'] is int ? json['importance'] : 1,
      confidence: (json['confidence'] ?? 1.0).toDouble(),
      source: json['source'] ?? 'user',
      createdAt: json['created_at'] ?? '',
      updatedAt: json['updated_at'] ?? '',
      lastAccessed: json['last_accessed'] ?? '',
      accessCount: json['access_count'] is int ? json['access_count'] : 0,
      status: json['status'] ?? 'ACTIVE',
      score: (json['score'] ?? 1.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'type': type,
      'content': content,
      'importance': importance,
      'confidence': confidence,
      'source': source,
      'created_at': createdAt,
      'updated_at': updatedAt,
      'last_accessed': lastAccessed,
      'access_count': accessCount,
      'status': status,
      'score': score,
    };
  }
}
