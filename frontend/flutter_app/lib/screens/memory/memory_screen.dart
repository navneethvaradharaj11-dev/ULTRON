import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/ultron_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/memory_provider.dart';

class MemoryScreen extends StatefulWidget {
  const MemoryScreen({super.key});

  @override
  State<MemoryScreen> createState() => _MemoryScreenState();
}

class _MemoryScreenState extends State<MemoryScreen> {
  final _memController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      final mem = Provider.of<MemoryProvider>(context, listen: false);
      if (auth.token != null) mem.fetchMemories(auth.token!);
    });
  }

  void _addMemory() {
    final text = _memController.text.trim();
    if (text.isEmpty) return;
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final mem = Provider.of<MemoryProvider>(context, listen: false);
    if (auth.token != null) {
      mem.addMemory(auth.token!, text, 'SEMANTIC', 3, 1.0);
      _memController.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final mem = Provider.of<MemoryProvider>(context);

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _memController,
                    decoration: const InputDecoration(hintText: 'Add new long-term fact...'),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(onPressed: _addMemory, child: const Text('ADD')),
              ],
            ),
            const SizedBox(height: 12),
            Expanded(
              child: mem.isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : ListView.builder(
                      itemCount: mem.memories.length,
                      itemBuilder: (context, index) {
                        final m = mem.memories[index];
                        return Card(
                          margin: const EdgeInsets.symmetric(vertical: 4),
                          child: ListTile(
                            leading: const Icon(Icons.psychology, color: UltronTheme.accentCyan),
                            title: Text(m.content, style: const TextStyle(fontSize: 14)),
                            subtitle: Text('Type: ${m.type} • Importance: ${m.importance}'),

                            trailing: IconButton(
                              icon: const Icon(Icons.delete, color: UltronTheme.error),
                              onPressed: () {
                                if (auth.token != null) mem.deleteMemory(auth.token!, m.id);
                              },
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
