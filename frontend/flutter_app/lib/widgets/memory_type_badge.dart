import 'package:flutter/material.dart';

class MemoryTypeBadge extends StatelessWidget {
  final String type;

  const MemoryTypeBadge({Key? key, required this.type}) : super(key: key);

  Color _getBadgeColor() {
    switch (type.toUpperCase()) {
      case 'WORKING':
        return Colors.amber.shade700;
      case 'EPISODIC':
        return Colors.purple.shade600;
      case 'SEMANTIC':
        return Colors.blue.shade600;
      case 'PROCEDURAL':
        return Colors.green.shade600;
      case 'PREFERENCE':
        return Colors.orange.shade700;
      default:
        return Colors.blueGrey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = _getBadgeColor();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(6.0),
        border: Border.all(color: color.withOpacity(0.4)),
      ),
      child: Text(
        type.toUpperCase(),
        style: TextStyle(
          color: color,
          fontSize: 11.0,
          fontWeight: FontWeight.bold,
          letterSpacing: 0.5,
        ),
      ),
    );
  }
}
