import 'package:flutter/material.dart';
import '../services/api_service.dart';

/// Lightweight summary of a single execution (from list endpoint)
class ExecutionItem {
  final String id;
  final String goal;
  final String status;
  final String createdAt;
  final String? startedAt;
  final String? completedAt;
  final String? idempotencyKey;
  final List<dynamic> tasks;

  const ExecutionItem({
    required this.id,
    required this.goal,
    required this.status,
    required this.createdAt,
    this.startedAt,
    this.completedAt,
    this.idempotencyKey,
    this.tasks = const [],
  });

  factory ExecutionItem.fromJson(Map<String, dynamic> json) {
    return ExecutionItem(
      id: json['id'] ?? '',
      goal: json['goal'] ?? '',
      status: json['status'] ?? 'PENDING',
      createdAt: json['created_at'] ?? '',
      startedAt: json['started_at'],
      completedAt: json['completed_at'],
      idempotencyKey: json['idempotency_key'],
      tasks: json['tasks'] ?? [],
    );
  }

  ExecutionItem copyWith({List<dynamic>? tasks, String? status}) {
    return ExecutionItem(
      id: id,
      goal: goal,
      status: status ?? this.status,
      createdAt: createdAt,
      startedAt: startedAt,
      completedAt: completedAt,
      idempotencyKey: idempotencyKey,
      tasks: tasks ?? this.tasks,
    );
  }
}

/// Full execution detail with tasks, events, and event consistency
class ExecutionDetail extends ExecutionItem {
  final List<ExecutionEventItem> events;
  final Map<String, dynamic>? eventConsistency;

  const ExecutionDetail({
    required super.id,
    required super.goal,
    required super.status,
    required super.createdAt,
    super.startedAt,
    super.completedAt,
    super.idempotencyKey,
    super.tasks,
    this.events = const [],
    this.eventConsistency,
  });

  factory ExecutionDetail.fromJson(Map<String, dynamic> json) {
    final base = ExecutionItem.fromJson(json);
    final rawEvents = json['events'] as List? ?? [];
    return ExecutionDetail(
      id: base.id,
      goal: base.goal,
      status: base.status,
      createdAt: base.createdAt,
      startedAt: base.startedAt,
      completedAt: base.completedAt,
      idempotencyKey: base.idempotencyKey,
      tasks: base.tasks,
      events: rawEvents.map((e) => ExecutionEventItem.fromJson(e)).toList(),
      eventConsistency: json['event_consistency'],
    );
  }
}

class ExecutionEventItem {
  final String id;
  final String eventType;
  final Map<String, dynamic>? payloadJson;
  final String createdAt;

  const ExecutionEventItem({
    required this.id,
    required this.eventType,
    this.payloadJson,
    required this.createdAt,
  });

  factory ExecutionEventItem.fromJson(Map<String, dynamic> json) {
    return ExecutionEventItem(
      id: json['id'] ?? '',
      eventType: json['event_type'] ?? '',
      payloadJson: json['payload_json'],
      createdAt: json['created_at'] ?? '',
    );
  }
}

/// Agent metrics from the /metrics endpoint
class AgentMetricItem {
  final String agentName;
  final int totalTasks;
  final int completed;
  final int failed;
  final int totalDurationMs;
  final int totalRetries;
  final double avgReviewConfidence;

  const AgentMetricItem({
    required this.agentName,
    required this.totalTasks,
    required this.completed,
    required this.failed,
    required this.totalDurationMs,
    required this.totalRetries,
    required this.avgReviewConfidence,
  });

  factory AgentMetricItem.fromJson(Map<String, dynamic> json) {
    return AgentMetricItem(
      agentName: json['agent_name'] ?? '',
      totalTasks: json['total_tasks'] ?? 0,
      completed: json['completed'] ?? 0,
      failed: json['failed'] ?? 0,
      totalDurationMs: json['total_duration_ms'] ?? 0,
      totalRetries: json['total_retries'] ?? 0,
      avgReviewConfidence: (json['avg_review_confidence'] ?? 0.0).toDouble(),
    );
  }

  double get successRate => totalTasks > 0 ? completed / totalTasks : 0.0;
  double get avgDurationSec => totalDurationMs / 1000.0;
}

// ---------------------------------------------------------------------------
// ExecutionProvider
// ---------------------------------------------------------------------------

class ExecutionProvider with ChangeNotifier {
  List<ExecutionItem> _executions = [];
  ExecutionDetail? _activeDetail;
  List<AgentMetricItem> _agentMetrics = [];
  bool _isLoading = false;
  String? _error;

  List<ExecutionItem> get executions => _executions;
  ExecutionDetail? get activeDetail => _activeDetail;
  List<AgentMetricItem> get agentMetrics => _agentMetrics;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // -----------------------------------------------------------------------
  // Fetch list
  // -----------------------------------------------------------------------
  Future<void> fetchExecutions(String token) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final res = await ApiService.get('/executions/', token: token);
      if (res != null) {
        _executions = (res as List).map((e) => ExecutionItem.fromJson(e)).toList();
      }
    } catch (e) {
      _error = e.toString();
    }
    _isLoading = false;
    notifyListeners();
  }

  // -----------------------------------------------------------------------
  // Fetch detail + event timeline
  // -----------------------------------------------------------------------
  Future<ExecutionDetail?> fetchExecutionDetail(String token, String executionId) async {
    try {
      final res = await ApiService.get('/executions/$executionId', token: token);
      if (res != null) {
        _activeDetail = ExecutionDetail.fromJson(res);
        notifyListeners();
        return _activeDetail;
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
    return null;
  }

  // -----------------------------------------------------------------------
  // Start new execution (with optional idempotency key)
  // -----------------------------------------------------------------------
  Future<void> startGoalExecution(String token, String goal, {String? idempotencyKey}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final body = <String, dynamic>{'goal': goal};
      if (idempotencyKey != null && idempotencyKey.isNotEmpty) {
        body['idempotency_key'] = idempotencyKey;
      }
      final res = await ApiService.post('/executions/', body, token: token);
      final item = ExecutionItem.fromJson(res);
      _executions.insert(0, item);
    } catch (e) {
      _error = e.toString();
    }
    _isLoading = false;
    notifyListeners();
  }

  // -----------------------------------------------------------------------
  // Cancel execution
  // -----------------------------------------------------------------------
  Future<void> cancelExecution(String token, String executionId) async {
    try {
      final res = await ApiService.post('/executions/$executionId/cancel', {}, token: token);
      final updated = ExecutionItem.fromJson(res);
      final idx = _executions.indexWhere((e) => e.id == executionId);
      if (idx != -1) _executions[idx] = updated;
      if (_activeDetail?.id == executionId) {
        await fetchExecutionDetail(token, executionId);
      }
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  // -----------------------------------------------------------------------
  // Resume execution (Phase 2.5)
  // -----------------------------------------------------------------------
  Future<void> resumeExecution(String token, String executionId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final res = await ApiService.post('/executions/$executionId/resume', {}, token: token);
      final updated = ExecutionItem.fromJson(res);
      final idx = _executions.indexWhere((e) => e.id == executionId);
      if (idx != -1) _executions[idx] = updated;
    } catch (e) {
      _error = e.toString();
    }
    _isLoading = false;
    notifyListeners();
  }

  // -----------------------------------------------------------------------
  // Fetch agent metrics (Phase 2.5)
  // -----------------------------------------------------------------------
  Future<void> fetchAgentMetrics(String token) async {
    try {
      final res = await ApiService.get('/executions/metrics', token: token);
      if (res != null) {
        _agentMetrics = (res as List).map((m) => AgentMetricItem.fromJson(m)).toList();
        notifyListeners();
      }
    } catch (_) {}
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
