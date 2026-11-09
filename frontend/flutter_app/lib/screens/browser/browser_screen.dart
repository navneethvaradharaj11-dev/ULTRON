import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/browser_provider.dart';
import 'browser_session_screen.dart';

class BrowserScreen extends StatefulWidget {
  const BrowserScreen({super.key});

  @override
  State<BrowserScreen> createState() => _BrowserScreenState();
}

class _BrowserScreenState extends State<BrowserScreen> {
  final TextEditingController _urlController = TextEditingController(text: 'https://example.com');

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<BrowserProvider>().fetchSessions();
    });
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<BrowserProvider>();

    return Scaffold(
      backgroundColor: const Color(0xFF12121C),
      appBar: AppBar(
        title: const Text('🌐 ULTRON Browser & Research Agent'),
        backgroundColor: const Color(0xFF1E1E2E),
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Address Bar Navigation Controls
            Card(
              color: const Color(0xFF1E1E2E),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _urlController,
                        style: const TextStyle(color: Colors.white, fontFamily: 'monospace'),
                        decoration: const InputDecoration(
                          hintText: 'Enter URL or search target...',
                          hintStyle: TextStyle(color: Colors.white38),
                          border: InputBorder.none,
                          icon: Icon(Icons.search, color: Colors.cyanAccent),
                        ),
                      ),
                    ),
                    ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.cyanAccent),
                      onPressed: () {
                        final url = _urlController.text.trim();
                        if (url.isNotEmpty) {
                          provider.createSession(initialUrl: url);
                        }
                      },
                      icon: const Icon(Icons.arrow_forward, color: Colors.black),
                      label: const Text('Open Session', style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold)),
                    )
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: provider.isLoading
                  ? const Center(child: CircularProgressIndicator(color: Colors.cyanAccent))
                  : provider.sessions.isEmpty
                      ? const Center(
                          child: Text(
                            'No active browser sessions.\nEnter a URL above to start browsing.',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.white54, fontSize: 16),
                          ),
                        )
                      : ListView.builder(
                          itemCount: provider.sessions.length,
                          itemBuilder: (context, index) {
                            final session = provider.sessions[index];
                            return Card(
                              color: const Color(0xFF2A2A3C),
                              margin: const EdgeInsets.symmetric(vertical: 8),
                              child: ListTile(
                                leading: const Icon(Icons.language, color: Colors.cyanAccent, size: 30),
                                title: Text(
                                  session['current_url'] ?? 'Session ${session['session_id']}',
                                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                                ),
                                subtitle: Text(
                                  'Steps: ${session['step_count']} | Status: ${session['status']}',
                                  style: const TextStyle(color: Colors.white70),
                                ),
                                trailing: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    IconButton(
                                      icon: const Icon(Icons.open_in_new, color: Colors.cyanAccent),
                                      onPressed: () {
                                        Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                            builder: (_) => BrowserSessionScreen(sessionId: session['session_id']),
                                          ),
                                        );
                                      },
                                    ),
                                    IconButton(
                                      icon: const Icon(Icons.close, color: Colors.redAccent),
                                      onPressed: () {
                                        provider.closeSession(session['session_id']);
                                      },
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
            )
          ],
        ),
      ),
    );
  }
}
