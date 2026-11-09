import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class BrowserProvider with ChangeNotifier {
  List<Map<String, dynamic>> _sessions = [];
  Map<String, dynamic>? _activeSession;
  final List<Map<String, dynamic>> _sources = [];
  bool _isLoading = false;
  String? _error;

  List<Map<String, dynamic>> get sessions => _sessions;
  Map<String, dynamic>? get activeSession => _activeSession;
  List<Map<String, dynamic>> get sources => _sources;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchSessions() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final res = await ApiService.get('/api/v1/browser/sessions');
      if (res != null && res['sessions'] != null) {
        _sessions = List<Map<String, dynamic>>.from(res['sessions']);
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> createSession({String? initialUrl}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final res = await ApiService.post('/api/v1/browser/sessions', {
        'initial_url': initialUrl,
      });
      if (res != null) {
        _activeSession = res;
        await fetchSessions();
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> navigate(String sessionId, String url) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final res = await ApiService.post('/api/v1/browser/sessions/$sessionId/navigate', {
        'url': url,
      });
      if (res != null) {
        _activeSession = res;
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> closeSession(String sessionId) async {
    try {
      await ApiService.post('/api/v1/browser/sessions/$sessionId/close', {});

      if (_activeSession != null && _activeSession!['session_id'] == sessionId) {
        _activeSession = null;
      }
      await fetchSessions();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
}
