import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  Function(Map<String, dynamic>)? onEvent;

  void connect(String conversationId, String token) {
    final uri = Uri.parse('ws://127.0.0.1:8000/ws/chat/$conversationId?token=$token');
    _channel = WebSocketChannel.connect(uri);

    _channel!.stream.listen(
      (data) {
        if (onEvent != null) {
          final decoded = jsonDecode(data);
          onEvent!(decoded);
        }
      },
      onError: (error) {
        if (onEvent != null) {
          onEvent!({'type': 'error', 'message': error.toString()});
        }
      },
      onDone: () {
        if (onEvent != null) {
          onEvent!({'type': 'disconnected'});
        }
      },
    );
  }

  void sendMessage(String text) {
    if (_channel != null) {
      _channel!.sink.add(jsonEncode({'message': text}));
    }
  }

  void disconnect() {
    _channel?.sink.close();
  }
}
