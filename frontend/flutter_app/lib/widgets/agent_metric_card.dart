import 'package:flutter/material.dart';
import '../models/learning_models.dart';

class AgentMetricCard extends StatelessWidget {
  final AgentMetricModel metric;

  const AgentMetricCard({super.key, required this.metric});

  @override
  Widget build(BuildContext context) {
    final succPct = (metric.successRate * 100).toInt();

    return Card(
      elevation: 2.0,
      margin: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 6.0),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10.0)),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Row(
          children: [
            CircleAvatar(
              backgroundColor: Colors.indigo.shade100,
              child: Icon(Icons.smart_toy_outlined, color: Colors.indigo.shade800),
            ),
            const SizedBox(width: 12.0),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    metric.agentName.toUpperCase(),
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0),
                  ),
                  const SizedBox(height: 4.0),
                  Text(
                    "Total Runs: ${metric.totalRuns} • Retries: ${metric.retryCount}",
                    style: TextStyle(color: Colors.grey.shade600, fontSize: 12.0),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  "$succPct%",
                  style: TextStyle(
                    fontSize: 16.0,
                    fontWeight: FontWeight.bold,
                    color: metric.successRate >= 0.8 ? Colors.green : Colors.orange,
                  ),
                ),
                Text(
                  "Success",
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
