import 'package:flutter/material.dart';
import '../models/code_models.dart';

class CodeOutputPanel extends StatelessWidget {
  final CodeExecution? execution;

  const CodeOutputPanel({
    super.key,
    required this.execution,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF11111B),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.white12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Terminal Header
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: const BoxDecoration(
              color: Color(0xFF181825),
              borderRadius: BorderRadius.vertical(top: Radius.circular(8)),
            ),
            child: Row(
              children: [
                const Icon(Icons.terminal, color: Colors.greenAccent, size: 18),
                const SizedBox(width: 8),
                const Text(
                  'EXECUTION OUTPUT & CONSOLE',
                  style: TextStyle(
                    color: Colors.greenAccent,
                    fontWeight: FontWeight.bold,
                    fontSize: 11,
                    letterSpacing: 1.0,
                  ),
                ),
                const Spacer(),
                if (execution != null) ...[
                  Text(
                    'STATUS: ${execution!.status}',
                    style: TextStyle(
                      color: execution!.status == 'COMPLETED'
                          ? Colors.greenAccent
                          : Colors.redAccent,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'DURATION: ${execution!.durationMs}ms',
                    style: const TextStyle(color: Colors.white54, fontSize: 10),
                  ),
                ],
              ],
            ),
          ),
          const Divider(height: 1, color: Colors.white10),

          // Console Text Body
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (execution == null)
                    const Text(
                      'No execution output available. Click Run/Execute to start sandbox execution.',
                      style: TextStyle(fontFamily: 'monospace', color: Colors.white38, fontSize: 12),
                    )
                  else ...[
                    if (execution!.stdout.isNotEmpty) ...[
                      const Text(
                        '--- STDOUT ---',
                        style: TextStyle(fontFamily: 'monospace', color: Colors.greenAccent, fontSize: 11),
                      ),
                      SelectableText(
                        execution!.stdout,
                        style: const TextStyle(fontFamily: 'monospace', color: Color(0xFFA6ADC8), fontSize: 12),
                      ),
                      const SizedBox(height: 8),
                    ],
                    if (execution!.stderr.isNotEmpty) ...[
                      const Text(
                        '--- STDERR ---',
                        style: TextStyle(fontFamily: 'monospace', color: Colors.redAccent, fontSize: 11),
                      ),
                      SelectableText(
                        execution!.stderr,
                        style: const TextStyle(fontFamily: 'monospace', color: Colors.redAccent, fontSize: 12),
                      ),
                    ],
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
