import 'package:flutter/material.dart';
import '../models/code_models.dart';

class CodeTestResultWidget extends StatelessWidget {
  final List<CodeTestItem> testResults;

  const CodeTestResultWidget({
    super.key,
    required this.testResults,
  });

  @override
  Widget build(BuildContext context) {
    final passedCount = testResults.where((t) => t.status == 'PASSED').length;

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF181825),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                const Icon(Icons.fact_check, color: Colors.blueAccent, size: 18),
                const SizedBox(width: 8),
                const Text(
                  'TEST SUITE RESULTS',
                  style: TextStyle(
                    color: Colors.blueAccent,
                    fontWeight: FontWeight.bold,
                    fontSize: 11,
                    letterSpacing: 1.0,
                  ),
                ),
                const Spacer(),
                if (testResults.isNotEmpty)
                  Text(
                    '$passedCount / ${testResults.length} PASSED',
                    style: TextStyle(
                      color: passedCount == testResults.length ? Colors.greenAccent : Colors.amberAccent,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
              ],
            ),
          ),
          const Divider(height: 1, color: Colors.white10),
          Expanded(
            child: testResults.isEmpty
                ? const Center(
                    child: Text(
                      'No test results recorded yet.',
                      style: TextStyle(color: Colors.white38, fontSize: 12),
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(8),
                    itemCount: testResults.length,
                    itemBuilder: (context, index) {
                      final item = testResults[index];
                      final isPassed = item.status == 'PASSED';

                      return Card(
                        color: const Color(0xFF1E1E2E),
                        margin: const EdgeInsets.symmetric(vertical: 4),
                        child: ListTile(
                          dense: true,
                          leading: Icon(
                            isPassed ? Icons.check_circle : Icons.cancel,
                            color: isPassed ? Colors.greenAccent : Colors.redAccent,
                            size: 18,
                          ),
                          title: Text(
                            item.testName,
                            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                          ),
                          subtitle: Text(
                            '${item.framework} • ${item.durationMs}ms',
                            style: const TextStyle(color: Colors.white54, fontSize: 10),
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
}
