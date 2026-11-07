import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/knowledge_models.dart';
import '../services/api_service.dart';

class KnowledgeProvider with ChangeNotifier {
  List<WorkspaceModel> _workspaces = [];
  WorkspaceModel? _activeWorkspace;
  List<KnowledgeSourceModel> _sources = [];
  List<KnowledgeSearchResultModel> _searchResults = [];
  List<String> _citations = [];
  bool _isLoading = false;
  String? _error;

  List<WorkspaceModel> get workspaces => _workspaces;
  WorkspaceModel? get activeWorkspace => _activeWorkspace;
  List<KnowledgeSourceModel> get sources => _sources;
  List<KnowledgeSearchResultModel> get searchResults => _searchResults;
  List<String> get citations => _citations;
  bool get isLoading => _isLoading;
  String? get error => _error;

  static String get baseUrl => '${ApiService.baseUrl}/knowledge';

  Future<void> fetchWorkspaces(String token) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/workspaces'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        final List list = jsonDecode(res.body);
        _workspaces = list.map((item) => WorkspaceModel.fromJson(item)).toList();
        if (_workspaces.isNotEmpty && _activeWorkspace == null) {
          _activeWorkspace = _workspaces.first;
          fetchSources(token, _activeWorkspace!.workspaceId);
        }
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> createWorkspace(String token, String name, String? description) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/workspaces'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json'
        },
        body: jsonEncode({'name': name, 'description': description}),
      );
      if (res.statusCode == 201) {
        fetchWorkspaces(token);
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> fetchSources(String token, String workspaceId) async {
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/sources?workspace_id=$workspaceId'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        final List list = jsonDecode(res.body);
        _sources = list.map((s) => KnowledgeSourceModel.fromJson(s)).toList();
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> searchKnowledge(String token, String query, {String? workspaceId}) async {
    _isLoading = true;
    notifyListeners();
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/search'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json'
        },
        body: jsonEncode({
          'query': query,
          'workspace_id': workspaceId ?? _activeWorkspace?.workspaceId,
          'top_k': 5
        }),
      );
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        final List list = data['results'] ?? [];
        _searchResults = list.map((r) => KnowledgeSearchResultModel.fromJson(r)).toList();
        _citations = List<String>.from(data['citations'] ?? []);
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> deleteSource(String token, String sourceId) async {
    try {
      final res = await http.delete(
        Uri.parse('$baseUrl/sources/$sourceId'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200 && _activeWorkspace != null) {
        fetchSources(token, _activeWorkspace!.workspaceId);
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
}
