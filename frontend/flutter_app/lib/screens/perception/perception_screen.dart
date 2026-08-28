import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/perception_provider.dart';
import '../../widgets/screenshot_view.dart';
import '../../widgets/visual_overlay.dart';
import '../../widgets/perception_element_card.dart';
import '../../widgets/confidence_indicator.dart';

class PerceptionScreen extends StatelessWidget {
  const PerceptionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<PerceptionProvider>(context);

    return Scaffold(
      backgroundColor: const Color(0xFF11111B),
      appBar: AppBar(
        backgroundColor: const Color(0xFF181825),
        title: Row(
          children: [
            const Icon(Icons.visibility, color: Colors.purpleAccent),
            const SizedBox(width: 8),
            const Text(
              'PERCEIVED STATE ENGINE',
              style: TextStyle(
                color: Colors.purpleAccent,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.2,
                fontSize: 16,
              ),
            ),
            const Spacer(),
            ConfidenceIndicatorWidget(confidence: provider.confidence),
          ],
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Expanded(
              flex: 3,
              child: Column(
                children: [
                  const ScreenshotViewWidget(screenshotId: 'latest_shot'),
                  const SizedBox(height: 12),
                  Expanded(
                    child: VisualOverlayWidget(elements: provider.elements),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              flex: 2,
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFF181825),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.white10),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'DETECTED UI COMPONENTS',
                      style: TextStyle(
                        color: Colors.cyanAccent,
                        fontWeight: FontWeight.bold,
                        fontSize: 11,
                        letterSpacing: 1.0,
                      ),
                    ),
                    const Divider(height: 1, color: Colors.white10),
                    Expanded(
                      child: provider.elements.isEmpty
                          ? const Center(
                              child: Text(
                                'No detected components.',
                                style: TextStyle(color: Colors.white38, fontSize: 12),
                              ),
                            )
                          : ListView.builder(
                              itemCount: provider.elements.length,
                              itemBuilder: (context, index) {
                                return PerceptionElementCard(element: provider.elements[index]);
                              },
                            ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
