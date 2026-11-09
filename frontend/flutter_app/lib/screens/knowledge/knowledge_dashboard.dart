import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/ultron_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/knowledge_provider.dart';

class KnowledgeDashboard extends StatefulWidget {
  const KnowledgeDashboard({super.key});

  @override
  State<KnowledgeDashboard> createState() => _KnowledgeDashboardState();
}

class _KnowledgeDashboardState extends State<KnowledgeDashboard> {
  final _queryController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      final kn = Provider.of<KnowledgeProvider>(context, listen: false);
      if (auth.token != null) {
        kn.fetchWorkspaces(auth.token!);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final knProv = Provider.of<KnowledgeProvider>(context);
    final auth = Provider.of<AuthProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Multimodal Knowledge Fabric'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              if (auth.token != null) knProv.fetchWorkspaces(auth.token!);
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Search Input Field
            TextField(
              controller: _queryController,
              decoration: InputDecoration(
                hintText: 'Search workspace knowledge (PDF, DOCX, XLSX, Code, Audio)...',
                suffixIcon: IconButton(
                  icon: const Icon(Icons.search, color: UltronTheme.primaryNeon),
                  onPressed: () {
                    final q = _queryController.text.trim();
                    if (q.isNotEmpty && auth.token != null) {
                      knProv.searchKnowledge(auth.token!, q);
                    }
                  },
                ),
              ),
            ),
            const SizedBox(height: 12.0),
            // Workspaces Bar
            Row(
              children: [
                const Text('Workspaces: ', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0)),
                Expanded(
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: knProv.workspaces.map((ws) {
                        return Padding(
                          padding: const EdgeInsets.only(right: 6.0),
                          child: Chip(
                            backgroundColor: UltronTheme.cardBg,
                            label: Text(ws.name, style: const TextStyle(fontSize: 12.0)),
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12.0),
            // Search Results Section
            if (knProv.searchResults.isNotEmpty) ...[
              const Text('Search Results & Provenance Citations', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0)),
              const SizedBox(height: 6.0),
              Expanded(
                child: ListView.builder(
                  itemCount: knProv.searchResults.length,
                  itemBuilder: (context, index) {
                    final res = knProv.searchResults[index];
                    return Card(
                      color: UltronTheme.cardBg,
                      margin: const EdgeInsets.symmetric(vertical: 4.0),
                      child: Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Text(res.citation, style: const TextStyle(color: UltronTheme.primaryNeon, fontWeight: FontWeight.bold, fontSize: 12.0)),
                                const Spacer(),
                                Text('Score: ${(res.score * 100).toInt()}%', style: const TextStyle(color: UltronTheme.textMuted, fontSize: 11.0)),
                              ],
                            ),
                            const SizedBox(height: 6.0),
                            Text(res.content, maxLines: 3, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 13.0)),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
            ] else ...[
              const Text('Workspace Sources', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0)),
              const SizedBox(height: 6.0),
              Expanded(
                child: knProv.sources.isEmpty
                    ? const Center(child: Text('No knowledge sources uploaded yet.', style: TextStyle(color: UltronTheme.textMuted)))
                    : ListView.builder(
                        itemCount: knProv.sources.length,
                        itemBuilder: (context, index) {
                          final src = knProv.sources[index];
                          return Card(
                            color: UltronTheme.cardBg,
                            child: ListTile(
                              leading: const Icon(Icons.description, color: UltronTheme.accentCyan),
                              title: Text(src.filename, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0)),
                              subtitle: Text('Type: ${src.sourceType} • Status: ${src.status}'),
                              trailing: IconButton(
                                icon: const Icon(Icons.delete_outline, color: UltronTheme.error),
                                onPressed: () {
                                  if (auth.token != null) knProv.deleteSource(auth.token!, src.sourceId);
                                },
                              ),
                            ),
                          );
                        },
                      ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
