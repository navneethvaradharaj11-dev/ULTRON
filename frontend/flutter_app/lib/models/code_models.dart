class CodeWorkspace {
  final String id;
  final String name;
  final String status;
  final String createdAt;
  final List<CodeFile> files;

  CodeWorkspace({
    required this.id,
    required this.name,
    required this.status,
    required this.createdAt,
    this.files = const [],
  });

  factory CodeWorkspace.fromJson(Map<String, dynamic> json) {
    return CodeWorkspace(
      id: json['id'] ?? '',
      name: json['name'] ?? 'default_workspace',
      status: json['status'] ?? 'ACTIVE',
      createdAt: json['created_at'] ?? '',
      files: (json['files'] as List<dynamic>?)
              ?.map((f) => CodeFile.fromJson(f))
              .toList() ??
          [],
    );
  }
}

class CodeFile {
  final String id;
  final String path;
  final String language;
  final String content;
  final int sizeBytes;

  CodeFile({
    required this.id,
    required this.path,
    required this.language,
    this.content = '',
    this.sizeBytes = 0,
  });

  factory CodeFile.fromJson(Map<String, dynamic> json) {
    return CodeFile(
      id: json['id'] ?? '',
      path: json['path'] ?? '',
      language: json['language'] ?? 'text',
      content: json['content'] ?? '',
      sizeBytes: json['size_bytes'] ?? 0,
    );
  }
}

class CodeExecution {
  final String id;
  final String workspaceId;
  final String executionId;
  final String language;
  final String status;
  final int? exitCode;
  final String stdout;
  final String stderr;
  final int durationMs;
  final int retryCount;

  CodeExecution({
    required this.id,
    required this.workspaceId,
    required this.executionId,
    required this.language,
    required this.status,
    this.exitCode,
    this.stdout = '',
    this.stderr = '',
    this.durationMs = 0,
    this.retryCount = 0,
  });

  factory CodeExecution.fromJson(Map<String, dynamic> json) {
    return CodeExecution(
      id: json['id'] ?? '',
      workspaceId: json['workspace_id'] ?? '',
      executionId: json['execution_id'] ?? '',
      language: json['language'] ?? 'python',
      status: json['status'] ?? 'CREATED',
      exitCode: json['exit_code'],
      stdout: json['stdout'] ?? '',
      stderr: json['stderr'] ?? '',
      durationMs: json['duration_ms'] ?? 0,
      retryCount: json['retry_count'] ?? 0,
    );
  }
}

class CodeArtifact {
  final String id;
  final String filename;
  final String mimeType;
  final int sizeBytes;
  final String? hashSha256;
  final String createdAt;

  CodeArtifact({
    required this.id,
    required this.filename,
    required this.mimeType,
    required this.sizeBytes,
    this.hashSha256,
    required this.createdAt,
  });

  factory CodeArtifact.fromJson(Map<String, dynamic> json) {
    return CodeArtifact(
      id: json['id'] ?? '',
      filename: json['filename'] ?? '',
      mimeType: json['mime_type'] ?? 'text/plain',
      sizeBytes: json['size_bytes'] ?? 0,
      hashSha256: json['hash_sha256'],
      createdAt: json['created_at'] ?? '',
    );
  }
}

class CodeTestItem {
  final String id;
  final String testName;
  final String framework;
  final String status;
  final String output;
  final int durationMs;

  CodeTestItem({
    required this.id,
    required this.testName,
    required this.framework,
    required this.status,
    required this.output,
    required this.durationMs,
  });

  factory CodeTestItem.fromJson(Map<String, dynamic> json) {
    return CodeTestItem(
      id: json['id'] ?? '',
      testName: json['test_name'] ?? '',
      framework: json['framework'] ?? '',
      status: json['status'] ?? 'UNKNOWN',
      output: json['output'] ?? '',
      durationMs: json['duration_ms'] ?? 0,
    );
  }
}
