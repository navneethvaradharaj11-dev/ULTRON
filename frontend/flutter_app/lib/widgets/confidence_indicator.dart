import 'package:flutter/material.dart';

class ConfidenceIndicatorWidget extends StatelessWidget {
  final double confidence;

  const ConfidenceIndicatorWidget({
    super.key,
    required this.confidence,
  });

  @override
  Widget build(BuildContext context) {
    final pct = (confidence * 100).toStringAsFixed(0);
    final color = confidence >= 0.85
        ? Colors.greenAccent
        : (confidence >= 0.60 ? Colors.amberAccent : Colors.redAccent);

    return Row(
      children: [
        const Icon(Icons.remove_red_eye, color: Colors.white70, size: 16),
        const SizedBox(width: 6),
        Text(
          'PERCEIVED CONFIDENCE: $pct%',
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.bold,
            fontSize: 11,
            letterSpacing: 1.0,
          ),
        ),
      ],
    );
  }
}
