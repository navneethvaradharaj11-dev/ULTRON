import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/ultron_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/workflow_provider.dart';
import 'workflow_detail_screen.dart';

class WorkflowDashboard extends StatefulWidget {
  const WorkflowDashboard({super.key});

  @override
  State<WorkflowDashboard> createState() => _WorkflowDashboardState();
}

class _WorkflowDashboardState extends State<WorkflowDashboard> {
  final _goalController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      final wf = Provider.of<WorkflowProvider>(context, listen: false);
      if (auth.token != null) {
        wf.fetchWorkflows(auth.token!);
      }
    });
  }

  void _showCreateDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: UltronTheme.cardBg,
        title: const Text('New Autonomous Workflow'),
        content: TextField(
          controller: _goalController,
          maxLines: 3,
          decoration: const InputDecoration(
            hintText: 'Enter autonomous goal (e.g. Research GPU architectures and generate report)...',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('CANCEL', style: TextStyle(color: UltronTheme.textMuted)),
          ),
          ElevatedButton(
            onPressed: () async {
              final goal = _goalController.text.trim();
              if (goal.isEmpty) return;
              final auth = Provider.of<AuthProvider>(context, listen: false);
              final wfProv = Provider.of<WorkflowProvider>(context, listen: false);
              if (auth.token != null) {
                final wf = await wfProv.createWorkflow(auth.token!, goal);
                _goalController.clear();
                if (mounted) {
                  if (ctx.mounted) Navigator.pop(ctx);
                  if (wf != null) {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => WorkflowDetailScreen(workflowId: wf.workflowId),
                      ),
                    );
                  }
                }

              }
            },
            child: const Text('CREATE & START'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final wfProv = Provider.of<WorkflowProvider>(context);
    final auth = Provider.of<AuthProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Autonomous Workflows'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              if (auth.token != null) wfProv.fetchWorkflows(auth.token!);
            },
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showCreateDialog,
        icon: const Icon(Icons.add),
        label: const Text('NEW WORKFLOW'),
      ),
      body: wfProv.isLoading
          ? const Center(child: CircularProgressIndicator())
          : wfProv.workflows.isEmpty
              ? const Center(
                  child: Text(
                    'No autonomous workflows created yet.',
                    style: TextStyle(color: UltronTheme.textMuted),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(12.0),
                  itemCount: wfProv.workflows.length,
                  itemBuilder: (context, index) {
                    final wf = wfProv.workflows[index];
                    return Card(
                      color: UltronTheme.cardBg,

                      margin: const EdgeInsets.symmetric(vertical: 6.0),
                      child: ListTile(
                        leading: const Icon(Icons.account_tree, color: UltronTheme.accentCyan),
                        title: Text(wf.goal, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0)),
                        subtitle: Text('State: ${wf.state} • Progress: ${(wf.progress * 100).toInt()}%'),
                        trailing: const Icon(Icons.chevron_right, color: UltronTheme.textMuted),
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => WorkflowDetailScreen(workflowId: wf.workflowId),
                            ),
                          );
                        },
                      ),
                    );
                  },
                ),
    );
  }
}
