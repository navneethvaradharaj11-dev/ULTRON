import 'package:flutter/material.dart';
import '../models/perception_models.dart';

class PerceptionElementCard extends StatelessWidget {
  final PerceptionElement element;

  const PerceptionElementCard({
    super.key,
    required this.element,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFF1E1E2E),
      margin: const EdgeInsets.symmetric(vertical: 4),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(6),
        side: BorderSide(
          color: element.sensitive ? Colors.redAccent : Colors.cyanAccent.withValues(alpha: 0.5),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Row(
          children: [
            Icon(
              _getElementIcon(element.type),
              color: element.sensitive ? Colors.redAccent : Colors.cyanAccent,
              size: 18,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    element.label.isEmpty ? element.id : element.label,
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                  Text(
                    'TYPE: ${element.type.toUpperCase()} • CONFIDENCE: ${(element.confidence * 100).toStringAsFixed(0)}%',
                    style: const TextStyle(color: Colors.white54, fontSize: 10),
                  ),
                ],
              ),
            ),
            if (element.sensitive)
              const Chip(
                label: Text('SENSITIVE', style: TextStyle(color: Colors.redAccent, fontSize: 9)),
                backgroundColor: Color(0x33FF5252),
              ),
          ],
        ),
      ),
    );
  }

  IconData _getElementIcon(String type) {
    if (type.contains('button')) return Icons.smart_button;
    if (type.contains('input') || type.contains('text')) return Icons.edit;
    if (type.contains('checkbox')) return Icons.check_box;
    if (type.contains('dropdown')) return Icons.arrow_drop_down_circle;
    if (type.contains('link')) return Icons.link;
    if (type.contains('tab')) return Icons.tab;
    if (type.contains('dialog')) return Icons.web_asset;
    return Icons.widgets;
  }
}
