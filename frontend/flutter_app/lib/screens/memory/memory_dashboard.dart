import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/memory_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/memory_card.dart';

class MemoryDashboardScreen extends StatefulWidget {
  static const routeName = '/memory-dashboard';

  const MemoryDashboardScreen({super.key});

  @override
  State<MemoryDashboardScreen> createState() => _MemoryDashboardScreenState();
}

class _MemoryDashboardScreenState extends State<MemoryDashboardScreen> {
  final TextEditingController _searchController = TextEditingController();
  final TextEditingController _addController = TextEditingController();
  String _selectedType = 'ALL';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _load();
    });
  }

  void _load() {
    final token = Provider.of<AuthProvider>(context, listen: false).token;
    if (token != null) {
      Provider.of<MemoryProvider>(context, listen: false).fetchMemories(token, type: _selectedType);
    }
  }

  void _showAddDialog() {
    String type = 'SEMANTIC';
    int importance = 3;
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Remember New Memory'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _addController,
              decoration: const InputDecoration(labelText: 'Memory Content'),
              maxLines: 3,
            ),
            const SizedBox(height: 12.0),
            DropdownButtonFormField<String>(
              initialValue: type,
              items: ['WORKING', 'EPISODIC', 'SEMANTIC', 'PROCEDURAL', 'PREFERENCE']

                  .map((t) => DropdownMenuItem(value: t, child: Text(t)))
                  .toList(),
              onChanged: (val) {
                if (val != null) type = val;
              },
              decoration: const InputDecoration(labelText: 'Category'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () {
              final token = Provider.of<AuthProvider>(context, listen: false).token;
              if (token != null && _addController.text.isNotEmpty) {
                Provider.of<MemoryProvider>(context, listen: false)
                    .addMemory(token, _addController.text, type, importance, 1.0);
                _addController.clear();
              }
              Navigator.pop(ctx);
            },
            child: const Text('Remember'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final memProvider = Provider.of<MemoryProvider>(context);
    final auth = Provider.of<AuthProvider>(context, listen: false);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Persistent Memory Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: _showAddDialog,
            tooltip: 'Remember New Memory',
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search memories...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.clear),
                  onPressed: () {
                    _searchController.clear();
                    _load();
                  },
                ),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(10.0)),
              ),
              onSubmitted: (val) {
                if (auth.token != null && val.isNotEmpty) {
                  memProvider.searchMemories(auth.token!, val);
                }
              },
            ),
          ),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12.0),
            child: Row(
              children: ['ALL', 'WORKING', 'EPISODIC', 'SEMANTIC', 'PROCEDURAL', 'PREFERENCE'].map((cat) {
                final selected = _selectedType == cat;
                return Padding(
                  padding: const EdgeInsets.only(right: 6.0),
                  child: FilterChip(
                    label: Text(cat),
                    selected: selected,
                    onSelected: (bool sel) {
                      setState(() {
                        _selectedType = cat;
                      });
                      _load();
                    },
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 8.0),
          Expanded(
            child: memProvider.isLoading
                ? const Center(child: CircularProgressIndicator())
                : memProvider.memories.isEmpty
                    ? const Center(child: Text('No memories found.'))
                    : ListView.builder(
                        itemCount: memProvider.memories.length,
                        itemBuilder: (ctx, i) {
                          final mem = memProvider.memories[i];
                          return MemoryCard(
                            memory: mem,
                            onForget: () {
                              if (auth.token != null) {
                                memProvider.forgetMemory(auth.token!, mem.id);
                              }
                            },
                            onDelete: () {
                              if (auth.token != null) {
                                memProvider.deleteMemory(auth.token!, mem.id);
                              }
                            },
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}
