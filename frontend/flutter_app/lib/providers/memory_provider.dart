import 'package:flutter/material.dart';
import '../models/memory_model.dart';
import '../services/api_service.dart';

class MemoryProvider with ChangeNotifier {
  List<MemoryModel> _memories = [];
  bool _isLoading = false;
  String _selectedCategory = 'ALL';

  List<MemoryModel> get memories => _memories;
  bool get isLoading => _isLoading;
  String get selectedCategory => _selectedCategory;

  void setSelectedCategory(String cat) {
    _selectedCategory = cat;
    notifyListeners();
  }

  Future<void> fetchMemories(String token, {String? type}) async {
    _isLoading = true;
    notifyListeners();
    try {
      final endpoint = type != null && type != 'ALL' ? '/api/v1/memory?type=$type' : '/api/v1/memory';
      final res = await ApiService.get(endpoint, token: token);
      if (res != null) {
        _memories = (res as List).map((m) => MemoryModel.fromJson(m)).toList();
      }
    } catch (_) {}
    _isLoading = false;
    notifyListeners();
  }

  Future<void> addMemory(String token, String content, String type, int importance, double confidence) async {
    try {
      final res = await ApiService.post('/api/v1/memory', {
        'content': content,
        'type': type,
        'importance': importance,
        'confidence': confidence,
        'source': 'user_explicit'
      }, token: token);
      if (res != null) {
        _memories.insert(0, MemoryModel.fromJson(res));
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> searchMemories(String token, String query) async {
    _isLoading = true;
    notifyListeners();
    try {
      final res = await ApiService.post('/api/v1/memory/search', {
        'query': query,
        'top_k': 10
      }, token: token);
      if (res != null) {
        _memories = (res as List).map((m) => MemoryModel.fromJson(m)).toList();
      }
    } catch (_) {}
    _isLoading = false;
    notifyListeners();
  }

  Future<void> forgetMemory(String token, String memoryId) async {
    try {
      await ApiService.post('/api/v1/memory/$memoryId/forget', {}, token: token);
      _memories.removeWhere((m) => m.id == memoryId);
      notifyListeners();
    } catch (_) {}
  }

  Future<void> deleteMemory(String token, String memoryId) async {
    try {
      await ApiService.delete('/api/v1/memory/$memoryId', token: token);
      _memories.removeWhere((m) => m.id == memoryId);
      notifyListeners();
    } catch (_) {}
  }
}
