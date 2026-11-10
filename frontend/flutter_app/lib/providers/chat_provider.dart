import 'dart:async';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
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
  Timer? _thinkingTimeoutTimer;

  List<ConversationModel> get conversations => _conversations;
  ConversationModel? get currentConversation => _currentConversation;
  List<MessageModel> get messages => _messages;
  bool get isThinking => _isThinking;
  String get activeAgent => _activeAgent;
  String get agentDetail => _agentDetail;
  Map<String, dynamic>? get pendingApproval => _pendingApproval;

  ChatProvider() {
    _wsService.onEvent = _handleWebSocketEvent;
    _wsService.onError = _handleWebSocketError;
    _wsService.onDone = _handleWebSocketDone;
  }

  void _resetThinking() {
    _thinkingTimeoutTimer?.cancel();
    _thinkingTimeoutTimer = null;
    _isThinking = false;
    _activeAgent = '';
    _agentDetail = '';
  }

  void _startThinkingTimer() {
    _thinkingTimeoutTimer?.cancel();
    _thinkingTimeoutTimer = Timer(const Duration(seconds: 25), () {
      if (_isThinking) {
        _resetThinking();
        _messages.add(MessageModel(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          senderType: 'assistant',
          senderName: 'Commander',
          content: '⚠️ Response timed out. The backend did not finish processing the request within 25 seconds.',
          createdAt: DateTime.now().toIso8601String(),
        ));
        notifyListeners();
      }
    });
  }

  void _handleWebSocketError(dynamic error) {
    if (_isThinking) {
      _resetThinking();
      _messages.add(MessageModel(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        senderType: 'assistant',
        senderName: 'System',
        content: '⚠️ WebSocket connection error. Please verify the backend connection and try again.',
        createdAt: DateTime.now().toIso8601String(),
      ));
      notifyListeners();
    }
  }

  void _handleWebSocketDone() {
    if (_isThinking) {
      _resetThinking();
      notifyListeners();
    }
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
      await selectConversation(newConv, token);
    } catch (_) {}
  }

  Future<void> selectConversation(ConversationModel conv, String token) async {
    // If selecting same conversation and messages already present, do not wipe
    if (_currentConversation?.id == conv.id && _messages.isNotEmpty) {
      if (!_wsService.isConnected) {
        _wsService.connect(conv.id, token);
      }
      return;
    }

    _currentConversation = conv;
    // Only clear if not in the middle of a command execution
    if (!_isThinking) {
      _messages.clear();
    }
    _wsService.connect(conv.id, token);
    notifyListeners();

    // Fetch persisted message history from server
    try {
      final res = await ApiService.get('/chat/conversations/${conv.id}/messages', token: token);
      if (res != null && res is List) {
        final serverMessages = res.map((c) => MessageModel.fromJson(c)).toList();
        if (!_isThinking && _messages.isEmpty) {
          _messages.addAll(serverMessages);
          notifyListeners();
        }
      }
    } catch (_) {}
  }

  Future<void> sendMessage(String text, {String? token}) async {
    if (text.trim().isEmpty) return;
    
    // Fallback: If token was not passed by caller, read saved JWT from preferences
    if (token == null || token.isEmpty) {
      try {
        final prefs = await SharedPreferences.getInstance();
        token = prefs.getString('jwt_token');
      } catch (_) {}
    }

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
    _startThinkingTimer();

    // Ensure conversation exists
    if (_currentConversation == null && token != null && token.isNotEmpty) {
      await startNewConversation(token);
    }

    // Connect WebSocket if disconnected
    if (!_wsService.isConnected && _currentConversation != null && token != null && token.isNotEmpty) {
      _wsService.connect(_currentConversation!.id, token);
      for (int i = 0; i < 5 && !_wsService.isConnected; i++) {
        await Future.delayed(const Duration(milliseconds: 100));
      }
    }

    final sent = _wsService.sendMessage(text);
    if (!sent) {
      // Fallback: If WebSocket cannot send, route via REST API
      if (token != null) {
        _agentDetail = 'Routing via REST fallback...';
        notifyListeners();
        try {
          final res = await ApiService.post('/ultron/command', {'message': text}, token: token);
          _resetThinking();
          if (res != null) {
            final summary = res['workflow_id'] != null
                ? 'Workflow ${res['workflow_id']} initiated (Status: ${res['status'] ?? 'RUNNING'}).'
                : 'Command accepted.';
            _messages.add(MessageModel(
              id: DateTime.now().millisecondsSinceEpoch.toString(),
              senderType: 'assistant',
              senderName: 'ULTRON',
              content: summary,
              createdAt: DateTime.now().toIso8601String(),
            ));
          } else {
            _messages.add(MessageModel(
              id: DateTime.now().millisecondsSinceEpoch.toString(),
              senderType: 'assistant',
              senderName: 'System',
              content: 'Failed to deliver command to ULTRON core.',
              createdAt: DateTime.now().toIso8601String(),
            ));
          }
          notifyListeners();
        } catch (e) {
          _resetThinking();
          _messages.add(MessageModel(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            senderType: 'assistant',
            senderName: 'System',
            content: 'Network error: could not deliver command ($e)',
            createdAt: DateTime.now().toIso8601String(),
          ));
          notifyListeners();
        }
      } else {
        _resetThinking();
        _messages.add(MessageModel(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          senderType: 'assistant',
          senderName: 'System',
          content: 'Not connected to ULTRON server. Please check connection.',
          createdAt: DateTime.now().toIso8601String(),
        ));
        notifyListeners();
      }
    }
  }

  void _handleWebSocketEvent(Map<String, dynamic> event) {
    final type = event['type'];

    if (type == 'message_start') {
      _startThinkingTimer();
      _isThinking = true;
      _messages.add(MessageModel(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        senderType: 'assistant',
        senderName: 'ULTRON',
        content: '',
        createdAt: DateTime.now().toIso8601String(),
      ));
    } else if (type == 'message_delta') {
      _startThinkingTimer();
      if (_messages.isNotEmpty && _messages.last.senderType == 'assistant') {
        _messages.last.content += (event['delta'] ?? '');
      } else {
        _messages.add(MessageModel(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          senderType: 'assistant',
          senderName: 'ULTRON',
          content: (event['delta'] ?? ''),
          createdAt: DateTime.now().toIso8601String(),
        ));
      }
    } else if (type == 'agent_started' || type == 'agent_progress') {
      _startThinkingTimer();
      _activeAgent = event['agent'] ?? 'Commander';
      _agentDetail = event['status'] ?? event['detail'] ?? '';
    } else if (type == 'tool_started' || type == 'tool_completed') {
      _startThinkingTimer();
      _activeAgent = 'Tool: ${event['tool_name'] ?? 'specialist'}';
      _agentDetail = type == 'tool_started' ? 'Executing tool...' : 'Tool completed.';
    } else if (type == 'approval_required') {
      _pendingApproval = event;
      _resetThinking();
    } else if (type == 'message_complete') {
      _resetThinking();
      if (event['full_content'] != null && _messages.isNotEmpty && _messages.last.senderType == 'assistant') {
        if (_messages.last.content.isEmpty) {
          _messages.last.content = event['full_content'];
        }
      }
    }

    notifyListeners();
  }

  Future<void> respondToApproval(String token, {required bool approved}) async {
    if (_pendingApproval == null) return;
    final approvalData = _pendingApproval!;
    final approvalId = approvalData['approval_id'] ?? approvalData['id'] ?? '';
    final workflowId = approvalData['workflow_id'] ?? '';

    try {
      if (workflowId.isNotEmpty) {
        await ApiService.post(
          '/workflows/$workflowId/approve',
          {
            'approval_id': approvalId,
            'approved': approved,
          },
          token: token,
        );
      } else {
        await ApiService.post(
          '/executions/approve',
          {
            'approval_id': approvalId,
            'action': approved ? 'approved' : 'denied',
          },
          token: token,
        );
      }
    } catch (_) {}

    _pendingApproval = null;
    notifyListeners();
  }

  void clearApproval() {
    _pendingApproval = null;
    notifyListeners();
  }

  @override
  void dispose() {
    _thinkingTimeoutTimer?.cancel();
    _wsService.disconnect();
    super.dispose();
  }
}
