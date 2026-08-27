import 'package:flutter/material.dart';
import '../models/memory_model.dart';
import '../services/api_service.dart';

class MemoryProvider with ChangeNotifier {
  List<MemoryModel> _memories = [];
  bool _isLoading = false;

  List<MemoryModel> get memories => _memories;
  bool get isLoading => _isLoading;

  Future<void> fetchMemories(String token) async {
    _isLoading = true;
    notifyListeners();
    try {
      final res = await ApiService.get('/memory/', token: token);
      if (res != null) {
        _memories = (res as List).map((m) => MemoryModel.fromJson(m)).toList();
      }
    } catch (_) {}
    _isLoading = false;
    notifyListeners();
  }

  Future<void> addMemory(String token, String content, int importance) async {
    try {
      final res = await ApiService.post('/memory/', {
        'content': content,
        'importance': importance,
      }, token: token);
      _memories.insert(0, MemoryModel.fromJson(res));
      notifyListeners();
    } catch (_) {}
  }

  Future<void> deleteMemory(String token, String memoryId) async {
    try {
      await ApiService.delete('/memory/$memoryId', token: token);
      _memories.removeWhere((m) => m.id == memoryId);
      notifyListeners();
    } catch (_) {}
  }
}
