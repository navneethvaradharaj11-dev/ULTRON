import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/integration_models.dart';

class IntegrationProvider with ChangeNotifier {
  List<IntegrationItemModel> _integrations = [];
  bool _isLoading = false;
  String? _error;

  List<IntegrationItemModel> get integrations => _integrations;
  bool get isLoading => _isLoading;
  String? get error => _error;

  static const String baseUrl = 'http://127.0.0.1:8000/api/v1/integrations';

  Future<void> fetchIntegrations(String token) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final res = await http.get(
        Uri.parse(baseUrl),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        final List list = jsonDecode(res.body);
        _integrations = list.map((item) => IntegrationItemModel.fromJson(item)).toList();
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> connectIntegration(String token, String integrationId) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/$integrationId/connect'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        fetchIntegrations(token);
      }
    } catch (_) {}
  }

  Future<void> disconnectIntegration(String token, String integrationId) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/$integrationId/disconnect'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        fetchIntegrations(token);
      }
    } catch (_) {}
  }
}
