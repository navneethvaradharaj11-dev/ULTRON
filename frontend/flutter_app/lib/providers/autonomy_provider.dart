import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/autonomy_models.dart';
import '../services/api_service.dart';

class AutonomyProvider with ChangeNotifier {
  List<AutonomyRuleModel> _rules = [];
  List<AutonomyNotificationModel> _notifications = [];
  bool _isLoading = false;
  String? _error;

  List<AutonomyRuleModel> get rules => _rules;
  List<AutonomyNotificationModel> get notifications => _notifications;
  bool get isLoading => _isLoading;
  String? get error => _error;

  static String get baseUrl => '${ApiService.baseUrl}/autonomy';

  Future<void> fetchRules(String token) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/rules'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        final List list = jsonDecode(res.body);
        _rules = list.map((item) => AutonomyRuleModel.fromJson(item)).toList();
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchNotifications(String token) async {
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/notifications'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        final List list = jsonDecode(res.body);
        _notifications = list.map((item) => AutonomyNotificationModel.fromJson(item)).toList();
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> toggleRule(String token, String ruleId, bool enable) async {
    final path = enable ? 'enable' : 'disable';
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/rules/$ruleId/$path'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        fetchRules(token);
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> createRule(String token, String name, String goalTemplate, String triggerType, String autonomyLevel) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/rules'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json'
        },
        body: jsonEncode({
          'name': name,
          'goal_template': goalTemplate,
          'trigger_type': triggerType,
          'autonomy_level': autonomyLevel
        }),
      );
      if (res.statusCode == 201) {
        fetchRules(token);
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
}
