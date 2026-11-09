import 'package:flutter/material.dart';
import '../core/theme/ultron_theme.dart';
import '../models/workflow_models.dart';

class WorkflowEventTimeline extends StatelessWidget {
  final List<WorkflowEventModel> events;

  const WorkflowEventTimeline({super.key, required this.events});

  @override
  Widget build(BuildContext context) {
    if (events.isEmpty) {
      return const Center(
        child: Text('No timeline events yet', style: TextStyle(color: UltronTheme.textMuted)),
      );
    }

    return ListView.builder(
      itemCount: events.length,
      itemBuilder: (context, index) {
        final evt = events[index];
        return Container(
          margin: const EdgeInsets.symmetric(vertical: 4.0),
          padding: const EdgeInsets.all(10.0),
          decoration: BoxDecoration(
            color: UltronTheme.cardBg,
            borderRadius: BorderRadius.circular(6.0),

            border: Border.all(color: UltronTheme.accentCyan.withValues(alpha: 0.2)),
          ),
          child: Row(
            children: [
              const Icon(Icons.timeline, color: UltronTheme.accentCyan, size: 16.0),
              const SizedBox(width: 8.0),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      evt.eventType,
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13.0),
                    ),
                    Text(
                      evt.createdAt,
                      style: const TextStyle(color: UltronTheme.textMuted, fontSize: 10.0),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
