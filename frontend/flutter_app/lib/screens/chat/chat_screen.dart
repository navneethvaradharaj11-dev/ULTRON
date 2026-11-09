import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/ultron_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/chat_provider.dart';
import '../../widgets/chat_bubble.dart';
import '../../widgets/thinking_indicator.dart';
import '../../widgets/voice_button.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _inputController = TextEditingController();
  final _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      final chat = Provider.of<ChatProvider>(context, listen: false);
      if (auth.token != null && chat.currentConversation == null) {
        chat.loadConversations(auth.token!).then((_) {
          if (!mounted) return;
          if (chat.currentConversation != null) return;
          if (chat.conversations.isNotEmpty) {
            chat.selectConversation(chat.conversations.first, auth.token!);
          } else {
            chat.startNewConversation(auth.token!);
          }
        });
      }
    });
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _send() {
    final text = _inputController.text.trim();
    if (text.isEmpty) return;
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final chat = Provider.of<ChatProvider>(context, listen: false);
    _inputController.clear();
    chat.sendMessage(text, token: auth.token);
    _scrollToBottom();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _inputController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final chat = Provider.of<ChatProvider>(context);

    // Auto-scroll when messages update or thinking state changes
    _scrollToBottom();

    return Scaffold(
      body: Column(
        children: [
          // Pending Approval Modal / Banner
          if (chat.pendingApproval != null) ...[
            Container(
              color: UltronTheme.warning.withValues(alpha: 0.2),
              padding: const EdgeInsets.all(12),
              margin: const EdgeInsets.all(8),
              child: Row(
                children: [
                  const Icon(Icons.warning, color: UltronTheme.warning),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'APPROVAL REQUIRED: ${chat.pendingApproval!['tool_name'] ?? chat.pendingApproval!['action_type'] ?? 'Sensitive Action'}',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                    ),
                  ),
                  TextButton(
                    onPressed: () {
                      final auth = Provider.of<AuthProvider>(context, listen: false);
                      if (auth.token != null) {
                        chat.respondToApproval(auth.token!, approved: false);
                      } else {
                        chat.clearApproval();
                      }
                    },
                    child: const Text('DENY', style: TextStyle(color: UltronTheme.error)),
                  ),
                  const SizedBox(width: 4),
                  ElevatedButton(
                    onPressed: () {
                      final auth = Provider.of<AuthProvider>(context, listen: false);
                      if (auth.token != null) {
                        chat.respondToApproval(auth.token!, approved: true);
                      } else {
                        chat.clearApproval();
                      }
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: UltronTheme.success,
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                    ),
                    child: const Text('APPROVE', style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
            ),
          ],
          Expanded(
            child: chat.messages.isEmpty && !chat.isThinking
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.psychology_outlined,
                          size: 48,
                          color: UltronTheme.primaryNeon.withValues(alpha: 0.4),
                        ),
                        const SizedBox(height: 12),
                        const Text(
                          'ULTRON Neural Chat Ready',
                          style: TextStyle(
                            color: UltronTheme.textMain,
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Type a command or query below to begin...',
                          style: TextStyle(
                            color: UltronTheme.textMuted,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    itemCount: chat.messages.length,
                    itemBuilder: (context, index) {
                      return ChatBubble(message: chat.messages[index]);
                    },
                  ),
          ),
          if (chat.isThinking) ...[
            ThinkingIndicator(agentName: chat.activeAgent, detail: chat.agentDetail),
          ],
          Container(
            padding: const EdgeInsets.all(8.0),
            color: const Color(0xFF0B0F19),
            child: Row(
              children: [
                VoiceButton(onVoiceInput: (val) {
                  _inputController.text = val;
                  _send();
                }),
                Expanded(
                  child: TextField(
                    controller: _inputController,
                    decoration: const InputDecoration(
                      hintText: 'Command ULTRON...',
                    ),
                    onSubmitted: (_) => _send(),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.send, color: UltronTheme.primaryNeon),
                  onPressed: _send,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
