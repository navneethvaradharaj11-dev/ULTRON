import 'package:flutter/material.dart';
import '../models/memory_model.dart';
import 'memory_type_badge.dart';
import 'memory_confidence_indicator.dart';

class MemoryCard extends StatelessWidget {
  final MemoryModel memory;
  final VoidCallback? onForget;
  final VoidCallback? onDelete;
  final VoidCallback? onTap;

  const MemoryCard({
    super.key,
    required this.memory,
    this.onForget,
    this.onDelete,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2.0,
      margin: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 6.0),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10.0)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(10.0),
        child: Padding(
          padding: const EdgeInsets.all(12.0),
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
              const SizedBox(height: 8.0),
              Text(
                memory.content,
                style: const TextStyle(fontSize: 14.0, fontWeight: FontWeight.w500),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 8.0),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    "Source: ${memory.source} • Importance: ${memory.importance}",
                    style: TextStyle(color: Colors.grey.shade600, fontSize: 11.0),
                  ),
                  Row(
                    children: [
                      if (onForget != null)
                        IconButton(
                          icon: const Icon(Icons.visibility_off_outlined, size: 18.0),
                          tooltip: 'Forget Memory',
                          onPressed: onForget,
                        ),
                      if (onDelete != null)
                        IconButton(
                          icon: const Icon(Icons.delete_outline, size: 18.0, color: Colors.redAccent),
                          tooltip: 'Delete Memory',
                          onPressed: onDelete,
                        ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
