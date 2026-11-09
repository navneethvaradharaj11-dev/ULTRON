import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/browser_provider.dart';
import '../../widgets/browser_view.dart';

class BrowserSessionScreen extends StatefulWidget {
  final String sessionId;

  const BrowserSessionScreen({super.key, required this.sessionId});

  @override
  State<BrowserSessionScreen> createState() => _BrowserSessionScreenState();
}

class _BrowserSessionScreenState extends State<BrowserSessionScreen> {
  final TextEditingController _urlController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<BrowserProvider>();
    final active = provider.activeSession;

    final url = active?['current_url'] ?? '';
    final page = active?['current_page'] ?? {};

    return Scaffold(
      backgroundColor: const Color(0xFF12121C),
      appBar: AppBar(
        title: Text('Session: ${widget.sessionId}'),
        backgroundColor: const Color(0xFF1E1E2E),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _urlController,
                    style: const TextStyle(color: Colors.white),
                    decoration: const InputDecoration(
                      hintText: 'Navigate URL...',
                      hintStyle: TextStyle(color: Colors.white38),
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send, color: Colors.cyanAccent),
                  onPressed: () {
                    if (_urlController.text.isNotEmpty) {
                      provider.navigate(widget.sessionId, _urlController.text.trim());
                    }
                  },
                )
              ],
            ),
            const SizedBox(height: 16),
            Expanded(
              child: BrowserView(
                url: url,
                title: page['title'] ?? 'Browser Page',
                pageText: page['text'] ?? 'Page content representation',
                elements: page['elements'] ?? [],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
