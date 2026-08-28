import 'package:flutter/material.dart';
import '../models/learning_models.dart';
import '../services/api_service.dart';

class LearningProvider with ChangeNotifier {
  List<StrategyModel> _strategies = [];
  List<AgentMetricModel> _metrics = [];
  List<LearningEventModel> _events = [];
  bool _isLoading = false;

  List<StrategyModel> get strategies => _strategies;
  List<AgentMetricModel> get metrics => _metrics;
  List<LearningEventModel> get events => _events;
  bool get isLoading => _isLoading;

  Future<void> fetchStrategies(String token) async {
    try {
      final res = await ApiService.get('/api/v1/learning/strategies', token: token);
      if (res != null) {
        _strategies = (res as List).map((s) => StrategyModel.fromJson(s)).toList();
      }
    } catch (_) {}
    notifyListeners();
  }

  Future<void> fetchAgentMetrics(String token) async {
    try {
      final res = await ApiService.get('/api/v1/agents/metrics', token: token);
      if (res != null) {
        _metrics = (res as List).map((m) => AgentMetricModel.fromJson(m)).toList();
      }
    } catch (_) {}
    notifyListeners();
  }

  Future<void> fetchLearningEvents(String token) async {
    _isLoading = true;
    notifyListeners();
    try {
      final res = await ApiService.get('/api/v1/learning/events', token: token);
      if (res != null) {
        _events = (res as List).map((e) => LearningEventModel.fromJson(e)).toList();
      }
    } catch (_) {}
    _isLoading = false;
    notifyListeners();
  }
}
