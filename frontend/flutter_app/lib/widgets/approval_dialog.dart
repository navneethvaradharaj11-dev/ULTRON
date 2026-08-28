import 'package:flutter/material.dart';
import '../models/perception_models.dart';

class ApprovalDialogWidget extends StatelessWidget {
  final ComputerActionItem action;
  final VoidCallback onApprove;
  final VoidCallback onReject;

  const ApprovalDialogWidget({
    super.key,
    required this.action,
    required this.onApprove,
    required this.onReject,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: const Color(0xFF1E1E2E),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: Colors.amberAccent),
      ),
      title: const Row(
        children: [
          Icon(Icons.gavel, color: Colors.amberAccent),
          SizedBox(width: 8),
          Text('SENSITIVE ACTION APPROVAL', style: TextStyle(color: Colors.amberAccent, fontSize: 14, fontWeight: FontWeight.bold)),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('ULTRON requests approval to execute high-impact computer action: ${action.actionType}', style: const TextStyle(color: Colors.white, fontSize: 12)),
          const SizedBox(height: 8),
          Text('Action ID: ${action.actionId}', style: const TextStyle(color: Colors.white54, fontSize: 10, fontFamily: 'monospace')),
        ],
      ),
      actions: [
        TextButton(
          onPressed: onReject,
          child: const Text('REJECT', style: TextStyle(color: Colors.redAccent)),
        ),
        ElevatedButton(
          style: ElevatedButton.styleFrom(backgroundColor: Colors.greenAccent),
          onPressed: onApprove,
          child: const Text('APPROVE', style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }
}
