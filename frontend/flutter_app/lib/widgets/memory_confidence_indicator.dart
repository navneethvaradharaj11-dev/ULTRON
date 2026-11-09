import 'package:flutter/material.dart';

class MemoryConfidenceIndicator extends StatelessWidget {
  final double confidence;

  const MemoryConfidenceIndicator({super.key, required this.confidence});

  @override
  Widget build(BuildContext context) {
    final pct = (confidence * 100).toInt();
    final color = confidence >= 0.8
        ? Colors.green.shade600
        : (confidence >= 0.5 ? Colors.orange.shade700 : Colors.red.shade600);

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(Icons.shield_outlined, size: 14.0, color: color),
        const SizedBox(width: 4.0),
        Text(
          "$pct% Confidence",
          style: TextStyle(color: color, fontSize: 12.0, fontWeight: FontWeight.bold),
        ),
      ],
    );
  }
}
