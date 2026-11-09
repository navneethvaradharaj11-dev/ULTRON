import 'package:flutter/material.dart';
import '../core/theme/ultron_theme.dart';
import '../models/workflow_models.dart';

class WorkflowResultCard extends StatelessWidget {
  final WorkflowResultModel result;

  const WorkflowResultCard({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: UltronTheme.cardBg,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.check_circle_outline, color: UltronTheme.success),
                const SizedBox(width: 8.0),
                const Text(
                  'Workflow Execution Result',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16.0),
                ),
                const Spacer(),
                Text(
                  'Confidence: ${(result.confidence * 100).toInt()}%',
                  style: const TextStyle(color: UltronTheme.accentCyan, fontSize: 12.0),
                ),
              ],
            ),
            const Divider(color: UltronTheme.textMuted),
            const SizedBox(height: 8.0),
            Text(
              result.summary,
              style: const TextStyle(fontSize: 14.0),
            ),
            const SizedBox(height: 12.0),
            Row(
              children: [
                Text(
                  'Completed Tasks: ${result.tasksCompleted}',
                  style: const TextStyle(color: UltronTheme.success, fontSize: 12.0),
                ),
                const SizedBox(width: 16.0),
                Text(
                  'Failed Tasks: ${result.tasksFailed}',
                  style: const TextStyle(color: UltronTheme.error, fontSize: 12.0),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
