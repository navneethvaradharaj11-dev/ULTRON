class WorkflowModel {
  final String workflowId;
  final String goal;
  final String state;
  final double progress;
  final String? currentStep;
  final int retryCount;
  final int replanCount;
  final String createdAt;
  final String updatedAt;
  final String? startedAt;
  final String? completedAt;

  WorkflowModel({
    required this.workflowId,
    required this.goal,
    required this.state,
    required this.progress,
    this.currentStep,
    required this.retryCount,
    required this.replanCount,
    required this.createdAt,
    required this.updatedAt,
    this.startedAt,
    this.completedAt,
  });

  factory WorkflowModel.fromJson(Map<String, dynamic> json) {
    return WorkflowModel(
      workflowId: json['workflow_id'] ?? json['id'] ?? '',
      goal: json['goal'] ?? '',
      state: json['state'] ?? json['current_state'] ?? 'CREATED',
      progress: (json['progress'] as num?)?.toDouble() ?? 0.0,
      currentStep: json['current_step'],
      retryCount: json['retry_count'] ?? 0,
      replanCount: json['replan_count'] ?? 0,
      createdAt: json['created_at'] ?? '',
      updatedAt: json['updated_at'] ?? '',
      startedAt: json['started_at'],
      completedAt: json['completed_at'],
    );
  }
}

class WorkflowStepModel {
  final String id;
  final String stepId;
  final String name;
  final String assignedAgent;
  final String status;
  final List<String> dependencies;
  final Map<String, dynamic>? inputData;
  final Map<String, dynamic>? outputData;
  final String? errorMessage;
  final int retryCount;
  final int durationMs;

  WorkflowStepModel({
    required this.id,
    required this.stepId,
    required this.name,
    required this.assignedAgent,
    required this.status,
    required this.dependencies,
    this.inputData,
    this.outputData,
    this.errorMessage,
    required this.retryCount,
    required this.durationMs,
  });

  factory WorkflowStepModel.fromJson(Map<String, dynamic> json) {
    return WorkflowStepModel(
      id: json['id'] ?? '',
      stepId: json['step_id'] ?? '',
      name: json['name'] ?? '',
      assignedAgent: json['assigned_agent'] ?? 'commander',
      status: json['status'] ?? 'PENDING',
      dependencies: List<String>.from(json['dependencies'] ?? json['dependencies_json'] ?? []),
      inputData: json['input_data'] ?? json['input_data_json'],
      outputData: json['output_data'] ?? json['output_data_json'],
      errorMessage: json['error_message'],
      retryCount: json['retry_count'] ?? 0,
      durationMs: json['duration_ms'] ?? 0,
    );
  }
}

class WorkflowEventModel {
  final String id;
  final String eventType;
  final Map<String, dynamic> payload;
  final String createdAt;

  WorkflowEventModel({
    required this.id,
    required this.eventType,
    required this.payload,
    required this.createdAt,
  });

  factory WorkflowEventModel.fromJson(Map<String, dynamic> json) {
    return WorkflowEventModel(
      id: json['id'] ?? '',
      eventType: json['event_type'] ?? '',
      payload: json['payload'] ?? {},
      createdAt: json['created_at'] ?? '',
    );
  }
}

class WorkflowResultModel {
  final String id;
  final String workflowId;
  final String summary;
  final String status;
  final double confidence;
  final Map<String, dynamic> evidence;
  final int tasksCompleted;
  final int tasksFailed;
  final List<String> warnings;

  WorkflowResultModel({
    required this.id,
    required this.workflowId,
    required this.summary,
    required this.status,
    required this.confidence,
    required this.evidence,
    required this.tasksCompleted,
    required this.tasksFailed,
    required this.warnings,
  });

  factory WorkflowResultModel.fromJson(Map<String, dynamic> json) {
    return WorkflowResultModel(
      id: json['id'] ?? '',
      workflowId: json['workflow_id'] ?? '',
      summary: json['summary'] ?? '',
      status: json['status'] ?? 'COMPLETED',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 1.0,
      evidence: json['evidence'] ?? {},
      tasksCompleted: json['tasks_completed'] ?? 0,
      tasksFailed: json['tasks_failed'] ?? 0,
      warnings: List<String>.from(json['warnings'] ?? []),
    );
  }
}

class WorkflowArtifactModel {
  final String id;
  final String filename;
  final String filePath;
  final String artifactType;
  final int sizeBytes;
  final String createdAt;

  WorkflowArtifactModel({
    required this.id,
    required this.filename,
    required this.filePath,
    required this.artifactType,
    required this.sizeBytes,
    required this.createdAt,
  });

  factory WorkflowArtifactModel.fromJson(Map<String, dynamic> json) {
    return WorkflowArtifactModel(
      id: json['id'] ?? '',
      filename: json['filename'] ?? '',
      filePath: json['file_path'] ?? json['filePath'] ?? '',
      artifactType: json['artifact_type'] ?? 'file',
      sizeBytes: json['size_bytes'] ?? 0,
      createdAt: json['created_at'] ?? '',
    );
  }
}

class WorkflowApprovalModel {
  final String id;
  final String workflowId;
  final String stepId;
  final String actionType;
  final String reason;
  final String status;
  final bool? approved;
  final String? decisionBy;
  final String createdAt;

  WorkflowApprovalModel({
    required this.id,
    required this.workflowId,
    required this.stepId,
    required this.actionType,
    required this.reason,
    required this.status,
    this.approved,
    this.decisionBy,
    required this.createdAt,
  });

  factory WorkflowApprovalModel.fromJson(Map<String, dynamic> json) {
    return WorkflowApprovalModel(
      id: json['id'] ?? '',
      workflowId: json['workflow_id'] ?? '',
      stepId: json['step_id'] ?? '',
      actionType: json['action_type'] ?? 'sensitive_operation',
      reason: json['reason'] ?? '',
      status: json['status'] ?? 'PENDING',
      approved: json['approved'],
      decisionBy: json['decision_by'],
      createdAt: json['created_at'] ?? '',
    );
  }
}

class AgentStatusModel {
  final String name;
  final String status;
  final String? currentTask;

  AgentStatusModel({
    required this.name,
    required this.status,
    this.currentTask,
  });

  factory AgentStatusModel.fromJson(Map<String, dynamic> json) {
    return AgentStatusModel(
      name: json['name'] ?? '',
      status: json['status'] ?? 'IDLE',
      currentTask: json['current_task'],
    );
  }
}

class ResearchSourceModel {
  final String title;
  final String url;
  final String snippet;

  ResearchSourceModel({
    required this.title,
    required this.url,
    required this.snippet,
  });

  factory ResearchSourceModel.fromJson(Map<String, dynamic> json) {
    return ResearchSourceModel(
      title: json['title'] ?? '',
      url: json['url'] ?? '',
      snippet: json['snippet'] ?? '',
    );
  }
}
