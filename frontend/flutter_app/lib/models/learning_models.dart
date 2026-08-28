class StrategyModel {
  final String strategyId;
  final String goalType;
  final String description;
  final List<dynamic> steps;
  final List<String> agents;
  final List<String> tools;
  final double successRate;
  final int sampleCount;
  final int averageDuration;
  final double failureRate;
  final double confidence;

  StrategyModel({
    required this.strategyId,
    required this.goalType,
    required this.description,
    required this.steps,
    required this.agents,
    required this.tools,
    required this.successRate,
    required this.sampleCount,
    required this.averageDuration,
    required this.failureRate,
    required this.confidence,
  });

  factory StrategyModel.fromJson(Map<String, dynamic> json) {
    return StrategyModel(
      strategyId: json['strategy_id'] ?? '',
      goalType: json['goal_type'] ?? '',
      description: json['description'] ?? '',
      steps: json['steps'] ?? [],
      agents: List<String>.from(json['agents'] ?? []),
      tools: List<String>.from(json['tools'] ?? []),
      successRate: (json['success_rate'] ?? 1.0).toDouble(),
      sampleCount: json['sample_count'] ?? 1,
      averageDuration: json['average_duration'] ?? 0,
      failureRate: (json['failure_rate'] ?? 0.0).toDouble(),
      confidence: (json['confidence'] ?? 1.0).toDouble(),
    );
  }
}


class AgentMetricModel {
  final String agentName;
  final int totalRuns;
  final int successfulRuns;
  final int failedRuns;
  final double successRate;
  final double failureRate;
  final int averageDuration;
  final int retryCount;
  final Map<String, dynamic> toolUsage;
  final double reviewScore;

  AgentMetricModel({
    required this.agentName,
    required this.totalRuns,
    required this.successfulRuns,
    required this.failedRuns,
    required this.successRate,
    required this.failureRate,
    required this.averageDuration,
    required this.retryCount,
    required this.toolUsage,
    required this.reviewScore,
  });

  factory AgentMetricModel.fromJson(Map<String, dynamic> json) {
    return AgentMetricModel(
      agentName: json['agent_name'] ?? '',
      totalRuns: json['total_runs'] ?? 0,
      successfulRuns: json['successful_runs'] ?? 0,
      failedRuns: json['failed_runs'] ?? 0,
      successRate: (json['success_rate'] ?? 1.0).toDouble(),
      failureRate: (json['failure_rate'] ?? 0.0).toDouble(),
      averageDuration: json['average_duration'] ?? 0,
      retryCount: json['retry_count'] ?? 0,
      toolUsage: json['tool_usage'] ?? {},
      reviewScore: (json['review_score'] ?? 1.0).toDouble(),
    );
  }
}


class LearningEventModel {
  final String id;
  final String userId;
  final String? executionId;
  final String eventType;
  final Map<String, dynamic> observation;
  final String patternDetected;
  final Map<String, dynamic> actionTaken;
  final String createdAt;

  LearningEventModel({
    required this.id,
    required this.userId,
    this.executionId,
    required this.eventType,
    required this.observation,
    required this.patternDetected,
    required this.actionTaken,
    required this.createdAt,
  });

  factory LearningEventModel.fromJson(Map<String, dynamic> json) {
    return LearningEventModel(
      id: json['id'] ?? '',
      userId: json['user_id'] ?? '',
      executionId: json['execution_id'],
      eventType: json['event_type'] ?? '',
      observation: json['observation'] ?? {},
      patternDetected: json['pattern_detected'] ?? 'Direct Execution Pattern',
      actionTaken: json['action_taken'] ?? {},
      createdAt: json['created_at'] ?? '',
    );
  }
}
