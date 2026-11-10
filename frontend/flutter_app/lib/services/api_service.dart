import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class ApiService {
  static const String _envUrl = String.fromEnvironment('API_BASE_URL', defaultValue: '');
  static String? customBaseUrl;

  static String get baseUrl {
    if (customBaseUrl != null && customBaseUrl!.isNotEmpty) {
      return customBaseUrl!;
    }
    if (_envUrl.isNotEmpty) {
      return _envUrl;
    }
    if (kIsWeb && Uri.base.host.isNotEmpty) {
      final host = Uri.base.host;
      final protocol = Uri.base.scheme == 'https' ? 'https' : 'http';
      return '$protocol://$host:8000/api/v1';
    }
    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.windows) {
      return 'http://127.0.0.1:8000/api/v1';
    }
    return 'http://100.69.161.16:8000/api/v1';
  }

  static String get wsBaseUrl {
    final base = baseUrl;
    if (base.startsWith('https://')) {
      return base.replaceFirst('https://', 'wss://');
    } else if (base.startsWith('http://')) {
      return base.replaceFirst('http://', 'ws://');
    }
    return 'ws://$base';
  }


  static Map<String, String> _headers(String? token) {
    final map = {'Content-Type': 'application/json'};
    if (token != null && token.isNotEmpty) {
      map['Authorization'] = 'Bearer $token';
    }
    return map;
  }

  static Future<dynamic> get(String endpoint, {String? token}) async {
    return _withRetry(() async {
      final response = await http.get(
        Uri.parse('$baseUrl$endpoint'),
        headers: _headers(token),
      );
      return _processResponse(response);
    });
  }

  static Future<dynamic> post(String endpoint, Map<String, dynamic> body, {String? token}) async {
    return _withRetry(() async {
      final response = await http.post(
        Uri.parse('$baseUrl$endpoint'),
        headers: _headers(token),
        body: jsonEncode(body),
      );
      return _processResponse(response);
    });
  }

  static Future<T> _withRetry<T>(Future<T> Function() fn, {int maxRetries = 2}) async {
    int attempts = 0;
    while (true) {
      try {
        attempts++;
        return await fn();
      } catch (e) {
        if (attempts >= maxRetries) rethrow;
        await Future.delayed(Duration(milliseconds: 500 * attempts));
      }
    }
  }


  static Future<dynamic> delete(String endpoint, {String? token}) async {
    final response = await http.delete(
      Uri.parse('$baseUrl$endpoint'),
      headers: _headers(token),
    );
    return _processResponse(response);
  }

  static dynamic _processResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) return null;
      return jsonDecode(response.body);
    } else {
      final err = jsonDecode(response.body);
      throw Exception(err['detail'] ?? 'HTTP Error ${response.statusCode}');
    }
  }
}
