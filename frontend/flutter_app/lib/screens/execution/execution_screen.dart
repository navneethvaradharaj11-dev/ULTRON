import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/ultron_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/execution_provider.dart';
import '../../widgets/task_graph_widget.dart';

class ExecutionScreen extends StatefulWidget {
  const ExecutionScreen({Key? key}) : super(key: key);

  @override
  State<ExecutionScreen> createState() => _ExecutionScreenState();
}

class _ExecutionScreenState extends State<ExecutionScreen> {
  final _goalController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      final exec = Provider.of<ExecutionProvider>(context, listen: false);
      if (auth.token != null) exec.fetchExecutions(auth.token!);
    });
  }

  void _startExecution() {
    final goal = _goalController.text.trim();
    if (goal.isEmpty) return;
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final exec = Provider.of<ExecutionProvider>(context, listen: false);
    if (auth.token != null) {
      exec.startGoalExecution(auth.token!, goal);
      _goalController.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final exec = Provider.of<ExecutionProvider>(context);

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('AGENTIC GOAL EXECUTION', style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1.2, color: UltronTheme.primaryNeon)),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _goalController,
                    decoration: const InputDecoration(hintText: 'Enter autonomous goal (e.g. Research AI trends)...'),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(onPressed: _startExecution, child: const Text('EXECUTE')),
              ],
            ),
            const SizedBox(height: 16),
            Expanded(
              child: exec.isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : ListView.builder(
                      itemCount: exec.executions.length,
                      itemBuilder: (context, index) {
                        final e = exec.executions[index];
                        return Card(
                          margin: const EdgeInsets.symmetric(vertical: 6),
                          child: ExpansionTile(
                            leading: const Icon(Icons.account_tree, color: UltronTheme.accentCyan),
                            title: Text(e.goal, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                            subtitle: Text('Status: ${e.status} • Created: ${e.createdAt.split("T").first}'),
                            children: [
                              Padding(
                                padding: const EdgeInsets.all(12.0),
                                child: Column(
                                  children: [
                                    TaskGraphWidget(tasks: e.tasks),
                                    if (e.status == 'RUNNING' || e.status == 'PENDING') ...[
                                      const SizedBox(height: 10),
                                      ElevatedButton.icon(
                                        style: ElevatedButton.styleFrom(backgroundColor: UltronTheme.error),
                                        icon: const Icon(Icons.stop, color: Colors.white),
                                        label: const Text('CANCEL EXECUTION', style: TextStyle(color: Colors.white)),
                                        onPressed: () {
                                          if (auth.token != null) exec.cancelExecution(auth.token!, e.id);
                                        },
                                      ),
                                    ],
                                  ],
                                ),
                              ),
                            ],
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
