import 'package:flutter/material.dart';

class BrowserActionCard extends StatelessWidget {
  final String actionType;
  final Map<String, dynamic> params;
  final String status;
  final String timestamp;

  const BrowserActionCard({
    super.key,
    required this.actionType,
    required this.params,
    required this.status,
    required this.timestamp,
  });

  @override
  Widget build(BuildContext context) {
    final isApproval = status == 'REQUIRES_APPROVAL';
    return Card(
      color: isApproval ? Colors.amber.withValues(alpha: 0.15) : const Color(0xFF2A2A3C),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10),
        side: BorderSide(
          color: isApproval ? Colors.amber : Colors.cyanAccent.withValues(alpha: 0.2),
        ),
      ),
      margin: const EdgeInsets.symmetric(vertical: 6),
      child: ListTile(
        leading: Icon(
          isApproval ? Icons.warning_amber_rounded : Icons.touch_app_outlined,
          color: isApproval ? Colors.amber : Colors.cyanAccent,
        ),
        title: Text(
          actionType.replaceAll('_', ' ').toUpperCase(),
          style: TextStyle(
            color: isApproval ? Colors.amber : Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 14,
          ),
        ),
        subtitle: Text(
          params.toString(),
          style: const TextStyle(color: Colors.white70, fontSize: 12),
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: isApproval ? Colors.amber : Colors.green.withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            status,
            style: TextStyle(
              color: isApproval ? Colors.black : Colors.greenAccent,
              fontSize: 11,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }
}
