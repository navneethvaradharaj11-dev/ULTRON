import 'package:flutter/material.dart';
import '../models/perception_models.dart';
import 'computer_action_card.dart';

class ComputerTimelineWidget extends StatelessWidget {
  final List<ComputerActionItem> actions;

  const ComputerTimelineWidget({
    super.key,
    required this.actions,
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
                Icon(Icons.history, color: Colors.cyanAccent, size: 18),
                SizedBox(width: 8),
                Text(
                  'COMPUTER ACTION TIMELINE',
                  style: TextStyle(
                    color: Colors.cyanAccent,
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
            child: actions.isEmpty
                ? const Center(
                    child: Text(
                      'No computer actions recorded yet.',
                      style: TextStyle(color: Colors.white38, fontSize: 12),
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(8),
                    itemCount: actions.length,
                    itemBuilder: (context, index) {
                      return ComputerActionCard(action: actions[index]);
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
