import 'package:flutter/material.dart';

class ScreenshotViewWidget extends StatelessWidget {
  final String screenshotId;
  final int width;
  final int height;

  const ScreenshotViewWidget({
    super.key,
    required this.screenshotId,
    this.width = 1280,
    this.height = 800,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      height: 350,
      decoration: BoxDecoration(
        color: const Color(0xFF181825),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.3)),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.screenshot, color: Colors.cyanAccent, size: 48),
            const SizedBox(height: 12),
            Text(
              'VIEWPORT CAPTURE: ${width}x$height',
              style: const TextStyle(
                color: Colors.cyanAccent,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.1,
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'ID: $screenshotId',
              style: const TextStyle(color: Colors.white54, fontSize: 10),
            ),
          ],
        ),
      ),
    );
  }
}
