import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/code_provider.dart';
import '../../widgets/code_output_panel.dart';
import '../../widgets/code_execution_timeline.dart';
import '../../widgets/code_test_result.dart';
import '../../widgets/code_artifact_card.dart';

class CodeExecutionScreen extends StatelessWidget {
  const CodeExecutionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<CodeProvider>(context);

    return Scaffold(
      backgroundColor: const Color(0xFF11111B),
      appBar: AppBar(
        backgroundColor: const Color(0xFF181825),
        title: const Text(
          'SANDBOX EXECUTION MONITOR',
          style: TextStyle(
            color: Colors.greenAccent,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.2,
          ),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Expanded(
              flex: 3,
              child: Row(
                children: [
                  Expanded(
                    flex: 3,
                    child: CodeOutputPanel(execution: provider.currentExecution),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    flex: 2,
                    child: CodeExecutionTimeline(events: provider.timelineEvents),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              flex: 2,
              child: Row(
                children: [
                  Expanded(
                    flex: 1,
                    child: CodeTestResultWidget(testResults: provider.testResults),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    flex: 1,
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
                            'EXECUTION ARTIFACTS',
                            style: TextStyle(
                              color: Colors.amberAccent,
                              fontWeight: FontWeight.bold,
                              fontSize: 11,
                              letterSpacing: 1.0,
                            ),
                          ),
                          const Divider(height: 1, color: Colors.white10),
                          Expanded(
                            child: provider.artifacts.isEmpty
                                ? const Center(
                                    child: Text(
                                      'No generated artifacts.',
                                      style: TextStyle(color: Colors.white38, fontSize: 12),
                                    ),
                                  )
                                : ListView.builder(
                                    itemCount: provider.artifacts.length,
                                    itemBuilder: (context, index) {
                                      return CodeArtifactCard(artifact: provider.artifacts[index]);
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
          ],
        ),
      ),
    );
  }
}
