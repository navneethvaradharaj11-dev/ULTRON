import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/ultron_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/chat_provider.dart';
import '../../widgets/chat_bubble.dart';
import '../../widgets/thinking_indicator.dart';
import '../../widgets/voice_button.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({Key? key}) : super(key: key);

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _inputController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      final chat = Provider.of<ChatProvider>(context, listen: false);
      if (auth.token != null) {
        chat.loadConversations(auth.token!).then((_) {
          if (chat.conversations.isNotEmpty) {
            chat.selectConversation(chat.conversations.first, auth.token!);
          } else {
            chat.startNewConversation(auth.token!);
          }
        });
      }
    });
  }

  void _send() {
    final text = _inputController.text.trim();
    if (text.isEmpty) return;
    final chat = Provider.of<ChatProvider>(context, listen: false);
    chat.sendMessage(text);
    _inputController.clear();
  }

  @override
  Widget build(BuildContext context) {
    final chat = Provider.of<ChatProvider>(context);

    return Scaffold(
      body: Column(
        children: [
          // Pending Approval Modal / Banner
          if (chat.pendingApproval != null) ...[
            Container(
              color: UltronTheme.warning.withOpacity(0.2),
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
            child: ListView.builder(
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
