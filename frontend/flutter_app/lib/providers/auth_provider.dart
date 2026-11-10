import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import '../models/user_model.dart';

class AuthProvider with ChangeNotifier {
  String? _token;
  UserModel? _user;
  bool _isLoading = false;

  String? get token => _token;
  UserModel? get user => _user;
  bool get isAuthenticated => _token != null && _token!.isNotEmpty;
  bool get isLoading => _isLoading;

  Future<void> initAuth() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('jwt_token');
    if (_token != null) {
      try {
        final data = await ApiService.get('/auth/me', token: _token);
        _user = UserModel.fromJson(data);
      } catch (_) {
        await logout();
      }
    }
    // Auto-login default operator for local desktop/web experience if not authenticated
    if (!isAuthenticated) {
      try {
        await login('ultron_user', 'SecretPassword123');
      } catch (_) {}
    }
    notifyListeners();
  }

  Future<bool> login(String username, String password) async {
    _isLoading = true;
    notifyListeners();
    try {
      final res = await ApiService.post('/auth/login', {
        'username': username,
        'password': password,
      });
      // Handle OAuth2 form submission format if required
      _token = res['access_token'];
      _user = UserModel(id: res['user_id'], username: res['username'], email: '');
      
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('jwt_token', _token!);
      
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      rethrow;
    }
  }

  Future<bool> register(String username, String email, String password) async {
    _isLoading = true;
    notifyListeners();
    try {
      await ApiService.post('/auth/register', {
        'username': username,
        'email': email,
        'password': password,
      });
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      rethrow;
    }
  }

  Future<void> logout() async {
    _token = null;
    _user = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('jwt_token');
    notifyListeners();
  }
}
