import 'package:flutter/material.dart';
import '../services/websocket_service.dart';
import '../models/message_model.dart';
import '../models/conversation_model.dart';
import '../services/api_service.dart';

class ChatProvider with ChangeNotifier {
  final WebSocketService _wsService = WebSocketService();
  List<ConversationModel> _conversations = [];
  ConversationModel? _currentConversation;
  final List<MessageModel> _messages = [];
  
  bool _isThinking = false;
  String _activeAgent = '';
  String _agentDetail = '';
  Map<String, dynamic>? _pendingApproval;

  List<ConversationModel> get conversations => _conversations;
  ConversationModel? get currentConversation => _currentConversation;
  List<MessageModel> get messages => _messages;
  bool get isThinking => _isThinking;
  String get activeAgent => _activeAgent;
  String get agentDetail => _agentDetail;
  Map<String, dynamic>? get pendingApproval => _pendingApproval;

  ChatProvider() {
    _wsService.onEvent = _handleWebSocketEvent;
  }

  Future<void> loadConversations(String token) async {
    try {
      final res = await ApiService.get('/chat/conversations', token: token);
      if (res != null) {
        _conversations = (res as List).map((c) => ConversationModel.fromJson(c)).toList();
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> startNewConversation(String token) async {
    try {
      final res = await ApiService.post('/chat/conversations', {'title': 'New Conversation'}, token: token);
      final newConv = ConversationModel.fromJson(res);
      _conversations.insert(0, newConv);
      selectConversation(newConv, token);
    } catch (_) {}
  }

  void selectConversation(ConversationModel conv, String token) {
    _currentConversation = conv;
    _messages.clear();
    _wsService.disconnect();
    _wsService.connect(conv.id, token);
    notifyListeners();
  }

  void sendMessage(String text) {
    if (text.trim().isEmpty) return;
    
    _messages.add(MessageModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      senderType: 'user',
      senderName: 'You',
      content: text,
      createdAt: DateTime.now().toIso8601String(),
    ));
    _isThinking = true;
    _activeAgent = 'Commander';
    _agentDetail = 'Analyzing intent...';
    notifyListeners();

    _wsService.sendMessage(text);
  }

  void _handleWebSocketEvent(Map<String, dynamic> event) {
    final type = event['type'];

    if (type == 'message_start') {
      _isThinking = true;
      _messages.add(MessageModel(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        senderType: 'assistant',
        senderName: 'ULTRON',
        content: '',
        createdAt: DateTime.now().toIso8601String(),
      ));
    } else if (type == 'message_delta') {
      if (_messages.isNotEmpty && _messages.last.senderType == 'assistant') {
        _messages.last.content += (event['delta'] ?? '');
      }
    } else if (type == 'agent_started' || type == 'agent_progress') {
      _activeAgent = event['agent'] ?? 'Commander';
      _agentDetail = event['status'] ?? event['detail'] ?? '';
    } else if (type == 'approval_required') {
      _pendingApproval = event;
      _isThinking = false;
    } else if (type == 'message_complete') {
      _isThinking = false;
      _activeAgent = '';
      _agentDetail = '';
    }

    notifyListeners();
  }

  void clearApproval() {
    _pendingApproval = null;
    notifyListeners();
  }
}
