import 'package:flutter/material.dart';
import '../models/perception_models.dart';

class ComputerActionCard extends StatelessWidget {
  final ComputerActionItem action;

  const ComputerActionCard({
    super.key,
    required this.action,
  });

  @override
  Widget build(BuildContext context) {
    final isApproved = action.approvalState == 'AUTO_APPROVED' || action.approvalState == 'APPROVED';
    final isReqApproval = action.approvalState == 'REQUIRES_APPROVAL';

    return Card(
      color: const Color(0xFF1E1E2E),
      margin: const EdgeInsets.symmetric(vertical: 4),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(6),
        side: BorderSide(
          color: isReqApproval ? Colors.amberAccent : (isApproved ? Colors.greenAccent : Colors.redAccent),
        ),
      ),
      child: ListTile(
        dense: true,
        leading: Icon(
          _getActionIcon(action.actionType),
          color: isReqApproval ? Colors.amberAccent : (isApproved ? Colors.greenAccent : Colors.redAccent),
          size: 18,
        ),
        title: Text(
          'ACTION: ${action.actionType}',
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
        ),
        subtitle: Text(
          'STATUS: ${action.status} • APPROVAL: ${action.approvalState}',
          style: const TextStyle(color: Colors.white54, fontSize: 10),
        ),
      ),
    );
  }

  IconData _getActionIcon(String type) {
    if (type.contains('CLICK')) return Icons.mouse;
    if (type.contains('TYPE')) return Icons.keyboard;
    if (type.contains('MOVE')) return Icons.open_with;
    if (type.contains('SCROLL')) return Icons.unfold_more;
    if (type.contains('WAIT')) return Icons.hourglass_empty;
    return Icons.touch_app;
  }
}
