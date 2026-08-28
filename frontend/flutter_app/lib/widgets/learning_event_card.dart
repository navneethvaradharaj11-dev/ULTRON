import 'package:flutter/material.dart';
import '../models/learning_models.dart';

class LearningEventCard extends StatelessWidget {
  final LearningEventModel event;

  const LearningEventCard({Key? key, required this.event}) : super(key: key);

  @override
  Widget build(BuildContext context) {
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
                  event.eventType.replaceAll('_', ' '),
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13.0, color: Colors.deepOrange),
                ),
                Text(
                  event.createdAt.length >= 10 ? event.createdAt.substring(0, 10) : '',
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 11.0),
                ),
              ],
            ),
            const SizedBox(height: 6.0),
            Text(
              "Pattern: ${event.patternDetected}",
              style: const TextStyle(fontSize: 13.0, fontWeight: FontWeight.w500),
            ),
          ],
        ),
      ),
    );
  }
}
