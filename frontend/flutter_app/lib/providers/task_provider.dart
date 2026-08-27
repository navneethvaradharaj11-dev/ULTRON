import 'package:flutter/material.dart';
import '../models/task_model.dart';
import '../services/api_service.dart';

class TaskProvider with ChangeNotifier {
  List<TaskModel> _tasks = [];
  bool _isLoading = false;

  List<TaskModel> get tasks => _tasks;
  bool get isLoading => _isLoading;

  Future<void> fetchTasks(String token) async {
    _isLoading = true;
    notifyListeners();
    try {
      final res = await ApiService.get('/tasks/', token: token);
      if (res != null) {
        _tasks = (res as List).map((t) => TaskModel.fromJson(t)).toList();
      }
    } catch (_) {}
    _isLoading = false;
    notifyListeners();
  }

  Future<void> createTask(String token, String title, String description, String priority) async {
    try {
      final res = await ApiService.post('/tasks/', {
        'title': title,
        'description': description,
        'priority': priority,
      }, token: token);
      _tasks.insert(0, TaskModel.fromJson(res));
      notifyListeners();
    } catch (_) {}
  }
}
