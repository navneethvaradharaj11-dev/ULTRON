import 'package:flutter/material.dart';
import '../../models/memory_model.dart';
import '../../widgets/memory_type_badge.dart';
import '../../widgets/memory_confidence_indicator.dart';

class MemoryDetailScreen extends StatelessWidget {
  final MemoryModel memory;

  const MemoryDetailScreen({Key? key, required this.memory}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Memory Detail'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                MemoryTypeBadge(type: memory.type),
                MemoryConfidenceIndicator(confidence: memory.confidence),
              ],
            ),
            const SizedBox(height: 16.0),
            Text(
              memory.content,
              style: const TextStyle(fontSize: 16.0, fontWeight: FontWeight.w500),
            ),
            const Divider(height: 32.0),
            Text("ID: ${memory.id}", style: const TextStyle(color: Colors.grey)),
            Text("Source: ${memory.source}", style: const TextStyle(color: Colors.grey)),
            Text("Importance: ${memory.importance}/5", style: const TextStyle(color: Colors.grey)),
            Text("Access Count: ${memory.accessCount}", style: const TextStyle(color: Colors.grey)),
            Text("Created At: ${memory.createdAt}", style: const TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}
