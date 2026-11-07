import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/ultron_models.dart';
import '../services/api_service.dart';

class UltronProvider with ChangeNotifier {
  UltronSystemStatusModel? _status;
  List<UltronActivityModel> _activities = [];
  bool _isLoading = false;
  String? _error;

  UltronSystemStatusModel? get status => _status;
  List<UltronActivityModel> get activities => _activities;
  bool get isLoading => _isLoading;
  String? get error => _error;

  static String get baseUrl => '${ApiService.baseUrl}/ultron';

  Future<void> fetchStatus(String token) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/status'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        _status = UltronSystemStatusModel.fromJson(jsonDecode(res.body));
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchTimeline(String token) async {
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/timeline'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        final List list = jsonDecode(res.body);
        _activities = list.map((item) => UltronActivityModel.fromJson(item)).toList();
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<Map<String, dynamic>?> sendCommand(String token, String message) async {
    _isLoading = true;
    notifyListeners();
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/command'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json'
        },
        body: jsonEncode({'message': message}),
      );
      if (res.statusCode == 200) {
        fetchTimeline(token);
        return jsonDecode(res.body);
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
    return null;
  }
}
