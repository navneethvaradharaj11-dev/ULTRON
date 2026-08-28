class WorkspaceModel {
  final String workspaceId;
  final String name;
  final String? description;
  final String createdAt;

  WorkspaceModel({
    required this.workspaceId,
    required this.name,
    this.description,
    required this.createdAt,
  });

  factory WorkspaceModel.fromJson(Map<String, dynamic> json) {
    return WorkspaceModel(
      workspaceId: json['workspace_id'] ?? json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'],
      createdAt: json['created_at'] ?? '',
    );
  }
}

class KnowledgeSourceModel {
  final String sourceId;
  final String filename;
  final String sourceType;
  final int sizeBytes;
  final String status;
  final String createdAt;

  KnowledgeSourceModel({
    required this.sourceId,
    required this.filename,
    required this.sourceType,
    required this.sizeBytes,
    required this.status,
    required this.createdAt,
  });

  factory KnowledgeSourceModel.fromJson(Map<String, dynamic> json) {
    return KnowledgeSourceModel(
      sourceId: json['source_id'] ?? json['id'] ?? '',
      filename: json['filename'] ?? '',
      sourceType: json['source_type'] ?? 'FILE',
      sizeBytes: json['size_bytes'] ?? 0,
      status: json['status'] ?? 'PENDING',
      createdAt: json['created_at'] ?? '',
    );
  }
}

class KnowledgeSearchResultModel {
  final String chunkId;
  final String sourceId;
  final String filename;
  final String content;
  final String locationSpec;
  final String citation;
  final double score;

  KnowledgeSearchResultModel({
    required this.chunkId,
    required this.sourceId,
    required this.filename,
    required this.content,
    required this.locationSpec,
    required this.citation,
    required this.score,
  });

  factory KnowledgeSearchResultModel.fromJson(Map<String, dynamic> json) {
    return KnowledgeSearchResultModel(
      chunkId: json['chunk_id'] ?? '',
      sourceId: json['source_id'] ?? '',
      filename: json['filename'] ?? '',
      content: json['content'] ?? '',
      locationSpec: json['location_spec'] ?? 'Document',
      citation: json['citation'] ?? '',
      score: (json['final_score'] as num?)?.toDouble() ?? (json['score'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
