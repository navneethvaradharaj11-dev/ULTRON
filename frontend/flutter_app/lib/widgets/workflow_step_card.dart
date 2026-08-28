import 'package:flutter/material.dart';
import '../core/theme/ultron_theme.dart';
import '../models/workflow_models.dart';

class WorkflowStepCard extends StatelessWidget {
  final WorkflowStepModel step;

  const WorkflowStepCard({Key? key, required this.step}) : super(key: key);

  Color _getStatusColor() {
    switch (step.status.toUpperCase()) {
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
    final statusColor = _getStatusColor();

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
                Container(
                  width: 10,
                  height: 10,
                  decoration: BoxDecoration(color: statusColor, shape: BoxShape.circle),
                ),
                const SizedBox(width: 8.0),
                Expanded(
                  child: Text(
                    step.name,
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 2.0),
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(4.0),
                  ),
                  child: Text(
                    step.status,
                    style: TextStyle(color: statusColor, fontSize: 11.0, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6.0),
            Row(
              children: [
                Text(
                  'Agent: ${step.assignedAgent}',
                  style: const TextStyle(color: UltronTheme.textMuted, fontSize: 12.0),
                ),
                const Spacer(),
                if (step.retryCount > 0)
                  Text(
                    'Retries: ${step.retryCount}',
                    style: const TextStyle(color: UltronTheme.warning, fontSize: 11.0),
                  ),
              ],
            ),
            if (step.errorMessage != null && step.errorMessage!.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 6.0),
                child: Text(
                  'Error: ${step.errorMessage}',
                  style: const TextStyle(color: UltronTheme.error, fontSize: 12.0),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
