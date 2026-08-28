import 'package:flutter/material.dart';
import '../core/theme/ultron_theme.dart';
import '../models/workflow_models.dart';

class TaskGraphVisualization extends StatelessWidget {
  final List<WorkflowStepModel> steps;

  const TaskGraphVisualization({Key? key, required this.steps}) : super(key: key);

  Color _getStatusColor(String status) {
    switch (status.toUpperCase()) {
      case 'COMPLETED':
      case 'SUCCESS':
        return UltronTheme.success;
      case 'RUNNING':
        return UltronTheme.accentCyan;
      case 'FAILED':
      case 'ERROR':
        return UltronTheme.error;
      case 'WAITING_APPROVAL':
        return UltronTheme.warning;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (steps.isEmpty) {
      return const Center(
        child: Text('No DAG task graph available', style: TextStyle(color: UltronTheme.textMuted)),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(8.0),
      itemCount: steps.length,
      itemBuilder: (context, index) {
        final step = steps[index];
        final statusColor = _getStatusColor(step.status);

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
                    Icon(Icons.account_tree, color: statusColor, size: 18),
                    const SizedBox(width: 8.0),
                    Expanded(
                      child: Text(
                        'Step [${step.stepId}]: ${step.name}',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: statusColor.withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(4.0),
                      ),
                      child: Text(
                        step.status,
                        style: TextStyle(color: statusColor, fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6.0),
                Text(
                  'Assigned Agent: ${step.assignedAgent}',
                  style: const TextStyle(color: UltronTheme.accentCyan, fontSize: 12.0),
                ),
                if (step.dependencies.isNotEmpty) ...[
                  const SizedBox(height: 4.0),
                  Text(
                    'Prerequisites: ${step.dependencies.join(', ')}',
                    style: const TextStyle(color: UltronTheme.textMuted, fontSize: 11.0),
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }
}
