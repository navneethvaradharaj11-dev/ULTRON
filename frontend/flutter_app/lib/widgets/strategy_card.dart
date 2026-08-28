import 'package:flutter/material.dart';
import '../models/learning_models.dart';

class StrategyCard extends StatelessWidget {
  final StrategyModel strategy;

  const StrategyCard({Key? key, required this.strategy}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final succPct = (strategy.successRate * 100).toInt();

    return Card(
      elevation: 2.0,
      margin: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 6.0),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10.0)),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  strategy.goalType.toUpperCase(),
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0, color: Colors.blueAccent),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 2.0),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(6.0),
                  ),
                  child: Text(
                    "$succPct% Success",
                    style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 12.0),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6.0),
            Text(
              strategy.description,
              style: TextStyle(color: Colors.grey.shade800, fontSize: 13.0),
            ),
            const SizedBox(height: 8.0),
            Row(
              children: [
                Icon(Icons.history, size: 14.0, color: Colors.grey.shade600),
                const SizedBox(width: 4.0),
                Text(
                  "Samples: ${strategy.sampleCount} • Avg Duration: ${strategy.averageDuration}ms",
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 11.0),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
