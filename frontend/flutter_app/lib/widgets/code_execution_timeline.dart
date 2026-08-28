import 'package:flutter/material.dart';

class CodeExecutionTimeline extends StatelessWidget {
  final List<Map<String, dynamic>> events;

  const CodeExecutionTimeline({
    super.key,
    required this.events,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF181825),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.all(12),
            child: Row(
              children: [
                Icon(Icons.timeline, color: Colors.purpleAccent, size: 18),
                SizedBox(width: 8),
                Text(
                  'EXECUTION EVENT TIMELINE',
                  style: TextStyle(
                    color: Colors.purpleAccent,
                    fontWeight: FontWeight.bold,
                    fontSize: 11,
                    letterSpacing: 1.0,
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: Colors.white10),
          Expanded(
            child: events.isEmpty
                ? const Center(
                    child: Text(
                      'No execution events recorded.',
                      style: TextStyle(color: Colors.white38, fontSize: 12),
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(8),
                    itemCount: events.length,
                    itemBuilder: (context, index) {
                      final evt = events[index];
                      final type = evt['event_type'] ?? 'event';
                      final payload = evt['payload'] ?? {};

                      return Card(
                        color: const Color(0xFF1E1E2E),
                        margin: const EdgeInsets.symmetric(vertical: 4),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(6),
                          side: const BorderSide(color: Colors.white12),
                        ),
                        child: Padding(
                          padding: const EdgeInsets.all(8.0),
                          child: Row(
                            children: [
                              Icon(
                                _getEventIcon(type),
                                color: _getEventColor(type),
                                size: 16,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      type.toUpperCase(),
                                      style: TextStyle(
                                        color: _getEventColor(type),
                                        fontWeight: FontWeight.bold,
                                        fontSize: 11,
                                      ),
                                    ),
                                    Text(
                                      payload.toString(),
                                      style: const TextStyle(
                                        fontFamily: 'monospace',
                                        color: Colors.white70,
                                        fontSize: 11,
                                      ),
                                      maxLines: 2,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  IconData _getEventIcon(String type) {
    if (type.contains('start')) return Icons.play_arrow;
    if (type.contains('completed')) return Icons.check_circle;
    if (type.contains('failed')) return Icons.error;
    if (type.contains('compile')) return Icons.build;
    if (type.contains('test')) return Icons.bug_report;
    return Icons.info;
  }

  Color _getEventColor(String type) {
    if (type.contains('completed')) return Colors.greenAccent;
    if (type.contains('failed') || type.contains('error')) return Colors.redAccent;
    if (type.contains('compile')) return Colors.amberAccent;
    if (type.contains('test')) return Colors.cyanAccent;
    return Colors.purpleAccent;
  }
}
