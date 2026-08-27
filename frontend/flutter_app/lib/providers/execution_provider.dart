import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ExecutionItem {
  final String id;
  final String goal;
  final String status;
  final String createdAt;
  final List<dynamic> tasks;

  ExecutionItem({
    required this.id,
    required this.goal,
    required this.status,
    required this.createdAt,
    this.tasks = const [],
  });

  factory ExecutionItem.fromJson(Map<String, dynamic> json) {
    return ExecutionItem(
      id: json['id'] ?? '',
      goal: json['goal'] ?? '',
      status: json['status'] ?? 'PENDING',
      createdAt: json['created_at'] ?? '',
      tasks: json['tasks'] ?? [],
    );
  }
}

class ExecutionProvider with ChangeNotifier {
  List<ExecutionItem> _executions = [];
  ExecutionItem? _activeExecution;
  bool _isLoading = false;

  List<ExecutionItem> get executions => _executions;
  ExecutionItem? get activeExecution => _activeExecution;
  bool get isLoading => _isLoading;

  Future<void> fetchExecutions(String token) async {
    _isLoading = true;
    notifyListeners();
    try {
      final res = await ApiService.get('/executions/', token: token);
      if (res != null) {
        _executions = (res as List).map((e) => ExecutionItem.fromJson(e)).toList();
      }
    } catch (_) {}
    _isLoading = false;
    notifyListeners();
  }

  Future<void> startGoalExecution(String token, String goal) async {
    _isLoading = true;
    notifyListeners();
    try {
      final res = await ApiService.post('/executions/', {'goal': goal}, token: token);
      final item = ExecutionItem.fromJson(res);
      _executions.insert(0, item);
      _activeExecution = item;
    } catch (_) {}
    _isLoading = false;
    notifyListeners();
  }

  Future<void> cancelExecution(String token, String executionId) async {
    try {
      final res = await ApiService.post('/executions/$executionId/cancel', {}, token: token);
      final updated = ExecutionItem.fromJson(res);
      final idx = _executions.indexWhere((e) => e.id == executionId);
      if (idx != -1) _executions[idx] = updated;
      if (_activeExecution?.id == executionId) _activeExecution = updated;
      notifyListeners();
    } catch (_) {}
  }
}
