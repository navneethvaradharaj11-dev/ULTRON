import 'package:flutter/material.dart';
import '../models/perception_models.dart';

class VisualOverlayWidget extends StatelessWidget {
  final List<PerceptionElement> elements;

  const VisualOverlayWidget({
    super.key,
    required this.elements,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E2E),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.white12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'VISUAL BOUNDING OVERLAY',
            style: TextStyle(
              color: Colors.purpleAccent,
              fontWeight: FontWeight.bold,
              fontSize: 11,
              letterSpacing: 1.0,
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: elements.isEmpty
                ? const Center(
                    child: Text(
                      'No visual bounding boxes detected.',
                      style: TextStyle(color: Colors.white38, fontSize: 12),
                    ),
                  )
                : ListView.builder(
                    itemCount: elements.length,
                    itemBuilder: (context, index) {
                      final item = elements[index];
                      final bbox = item.bbox;

                      return Container(
                        margin: const EdgeInsets.symmetric(vertical: 4),
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: const Color(0xFF181825),
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(
                            color: item.sensitive ? Colors.redAccent : Colors.cyanAccent,
                          ),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              item.sensitive ? Icons.warning : Icons.crop_square,
                              color: item.sensitive ? Colors.redAccent : Colors.cyanAccent,
                              size: 16,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                '${item.type.toUpperCase()}: ${item.label.isEmpty ? item.id : item.label}',
                                style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                              ),
                            ),
                            Text(
                              '(${bbox['x'] ?? 0}, ${bbox['y'] ?? 0})',
                              style: const TextStyle(color: Colors.white54, fontSize: 10, fontFamily: 'monospace'),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
