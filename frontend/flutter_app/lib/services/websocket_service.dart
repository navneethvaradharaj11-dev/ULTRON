import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'api_service.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  final StreamController<dynamic> _controller = StreamController<dynamic>.broadcast();
  bool _isConnected = false;

  Function(Map<String, dynamic>)? onEvent;
  Function(dynamic)? onError;
  Function()? onDone;

  Stream<dynamic> get stream => _controller.stream;
  bool get isConnected => _isConnected;

  void connect(String conversationId, String token) {
    disconnect();
    final wsBase = ApiService.wsBaseUrl;
    final url = '$wsBase/ws/chat/$conversationId?token=$token';

    try {
      _channel = WebSocketChannel.connect(Uri.parse(url));
      _isConnected = true;
      _channel!.stream.listen(
        (data) {
          _isConnected = true;
          _controller.add(data);
          if (onEvent != null && data is String) {
            try {
              final Map<String, dynamic> jsonMap = jsonDecode(data);
              onEvent!(jsonMap);
            } catch (_) {}
          }
        },
        onError: (err) {
          _isConnected = false;
          _controller.addError(err);
          onError?.call(err);
        },
        onDone: () {
          _isConnected = false;
          onDone?.call();
        },
      );
    } catch (e) {
      _isConnected = false;
      _controller.addError(e);
      onError?.call(e);
    }
  }

  void connectWorkflowStream(String workflowId, String token) {
    disconnect();
    final wsBase = ApiService.wsBaseUrl;
    final url = '$wsBase/workflows/ws/stream/$workflowId?token=$token';

    try {
      _channel = WebSocketChannel.connect(Uri.parse(url));
      _isConnected = true;
      _channel!.stream.listen(
        (data) {
          _isConnected = true;
          _controller.add(data);
          if (onEvent != null && data is String) {
            try {
              final Map<String, dynamic> jsonMap = jsonDecode(data);
              onEvent!(jsonMap);
            } catch (_) {}
          }
        },
        onError: (err) {
          _isConnected = false;
          _controller.addError(err);
          onError?.call(err);
        },
        onDone: () {
          _isConnected = false;
          onDone?.call();
        },
      );
    } catch (e) {
      _isConnected = false;
      _controller.addError(e);
      onError?.call(e);
    }
  }

  bool sendMessage(String message) {
    return send(jsonEncode({
      'type': 'user_message',
      'message': message,
      'content': message,
      'text': message,
    }));
  }

  bool send(dynamic data) {
    if (_channel != null && _isConnected) {
      try {
        _channel!.sink.add(data);
        return true;
      } catch (_) {
        _isConnected = false;
        return false;
      }
    }
    return false;
  }

  void disconnect() {
    try {
      _channel?.sink.close();
    } catch (_) {}
    _channel = null;
    _isConnected = false;
  }
}
