import 'package:flutter/material.dart';
import '../core/theme/ultron_theme.dart';

class TaskGraphWidget extends StatelessWidget {
  final List<dynamic> tasks;

  const TaskGraphWidget({Key? key, required this.tasks}) : super(key: key);

  Color _getStatusColor(String status) {
    switch (status.toUpperCase()) {
      case 'COMPLETED':
        return UltronTheme.success;
      case 'RUNNING':
        return UltronTheme.primaryNeon;
      case 'REQUIRES_APPROVAL':
        return UltronTheme.warning;
      case 'FAILED':
      case 'CANCELLED':
        return UltronTheme.error;
      default:
        return UltronTheme.textMuted;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (tasks.isEmpty) {
      return const Padding(
        padding: EdgeInsets.all(16.0),
        child: Text('No task graph initialized.', style: TextStyle(color: UltronTheme.textMuted)),
      );
    }

    return Column(
      children: List.generate(tasks.length, (index) {
        final task = tasks[index];
        final status = task['status'] ?? 'PENDING';
        final statusColor = _getStatusColor(status);

        return Column(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF121826),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: statusColor.withOpacity(0.5)),
              ),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 14,
                    backgroundColor: statusColor.withOpacity(0.2),
                    child: Text('${index + 1}', style: TextStyle(color: statusColor, fontSize: 12, fontWeight: FontWeight.bold)),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          task['goal'] ?? 'Sub-task',
                          style: const TextStyle(color: UltronTheme.textMain, fontWeight: FontWeight.bold, fontSize: 13.5),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          'Agent: ${task['assigned_agent'] ?? 'commander'}',
                          style: const TextStyle(color: UltronTheme.textMuted, fontSize: 11),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: statusColor.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      status.toUpperCase(),
                      style: TextStyle(color: statusColor, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ),
            if (index < tasks.length - 1)
              const Icon(Icons.arrow_downward, size: 16, color: UltronTheme.textMuted),
          ],
        );
      }),
    );
  }
}
