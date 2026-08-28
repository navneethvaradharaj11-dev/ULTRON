import 'package:flutter/material.dart';
import '../core/theme/ultron_theme.dart';
import '../models/workflow_models.dart';

class ApprovalRequestCard extends StatelessWidget {
  final WorkflowApprovalModel approval;
  final Function(bool approved) onDecision;

  const ApprovalRequestCard({
    Key? key,
    required this.approval,
    required this.onDecision,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isPending = approval.status.toUpperCase() == 'PENDING';

    return Card(
      color: UltronTheme.cardBg,
      margin: const EdgeInsets.symmetric(vertical: 6.0),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.security, color: UltronTheme.warning, size: 20),
                const SizedBox(width: 8.0),
                const Text(
                  'Approval Required (Server-Side)',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0, color: UltronTheme.warning),
                ),
                const Spacer(),
                Text(
                  approval.status,
                  style: TextStyle(
                    color: isPending ? UltronTheme.warning : (approval.approved == true ? UltronTheme.success : UltronTheme.error),
                    fontSize: 12.0,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8.0),
            Text('Action: ${approval.actionType}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13.0)),
            Text('Reason: ${approval.reason}', style: const TextStyle(color: UltronTheme.textMuted, fontSize: 12.0)),
            const SizedBox(height: 12.0),
            if (isPending)
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  OutlinedButton(
                    style: OutlinedButton.styleFrom(foregroundColor: UltronTheme.error),
                    onPressed: () => onDecision(false),
                    child: const Text('DENY'),
                  ),
                  const SizedBox(width: 12.0),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(backgroundColor: UltronTheme.success, foregroundColor: Colors.white),
                    onPressed: () => onDecision(true),
                    child: const Text('APPROVE'),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
