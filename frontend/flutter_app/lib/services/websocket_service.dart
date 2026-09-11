import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'api_service.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  final StreamController<dynamic> _controller = StreamController<dynamic>.broadcast();
  bool _isConnected = false;
  Function(Map<String, dynamic>)? onEvent;

  Stream<dynamic> get stream => _controller.stream;
  bool get isConnected => _isConnected;

  void connect(String conversationId, String token) {
    final wsBase = ApiService.wsBaseUrl;
    final url = '$wsBase/ws/chat/$conversationId?token=$token';

    try {
      _channel = WebSocketChannel.connect(Uri.parse(url));
      _isConnected = true;
      _channel!.stream.listen(
        (data) {
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
        },
        onDone: () {
          _isConnected = false;
        },
      );
    } catch (e) {
      _isConnected = false;
      _controller.addError(e);
    }
  }

  void connectWorkflowStream(String workflowId, String token) {
    final wsBase = ApiService.wsBaseUrl;
    final url = '$wsBase/ws/workflows/$workflowId?token=$token';

    try {
      _channel = WebSocketChannel.connect(Uri.parse(url));
      _isConnected = true;
      _channel!.stream.listen(
        (data) {
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
        },
        onDone: () {
          _isConnected = false;
        },
      );
    } catch (e) {
      _isConnected = false;
      _controller.addError(e);
    }
  }

  void sendMessage(String message) {
    send(jsonEncode({'type': 'user_message', 'content': message}));
  }

  void send(dynamic data) {
    if (_channel != null && _isConnected) {
      _channel!.sink.add(data);
    }
  }

  void disconnect() {
    _channel?.sink.close();
    _isConnected = false;
  }
}
