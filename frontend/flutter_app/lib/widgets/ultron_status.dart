import 'package:flutter/material.dart';
import '../core/theme/ultron_theme.dart';

class UltronStatusCard extends StatelessWidget {
  const UltronStatusCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: UltronTheme.primaryNeon.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.memory, color: UltronTheme.primaryNeon, size: 28),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text(
                    'ULTRON CORE ENGINE',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.2,
                      color: UltronTheme.primaryNeon,
                    ),
                  ),
                  SizedBox(height: 4),
                  Text(
                    'Multi-Agent System Operational • MySQL Memory Active',
                    style: TextStyle(fontSize: 12, color: UltronTheme.textMuted),
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: UltronTheme.success.withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                'ONLINE',
                style: TextStyle(
                  color: UltronTheme.success,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
