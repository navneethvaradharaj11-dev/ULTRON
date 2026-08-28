import 'package:flutter/material.dart';

class CodeEditor extends StatelessWidget {
  final String filename;
  final String content;
  final String language;
  final bool isReadOnly;
  final String? diffText;
  final ValueChanged<String>? onChanged;

  const CodeEditor({
    super.key,
    required this.filename,
    required this.content,
    this.language = 'text',
    this.isReadOnly = false,
    this.diffText,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final lines = content.split('\n');

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E2E),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header File Tab Bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: const BoxDecoration(
              color: Color(0xFF181825),
              borderRadius: BorderRadius.vertical(top: Radius.circular(8)),
            ),
            child: Row(
              children: [
                const Icon(Icons.code, color: Colors.cyanAccent, size: 18),
                const SizedBox(width: 8),
                Text(
                  filename,
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.cyanAccent.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    language.toUpperCase(),
                    style: const TextStyle(
                      color: Colors.cyanAccent,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: Colors.white10),

          // Code Content area with line numbers
          Expanded(
            child: diffText != null && diffText!.isNotEmpty
                ? _buildDiffView(diffText!)
                : SingleChildScrollView(
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Line Numbers Column
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                          color: const Color(0xFF11111B),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: List.generate(
                              lines.length,
                              (idx) => Text(
                                '${idx + 1}',
                                style: const TextStyle(
                                  fontFamily: 'monospace',
                                  color: Colors.white38,
                                  fontSize: 12,
                                ),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        // Code lines
                        Expanded(
                          child: Padding(
                            padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
                            child: SelectableText(
                              content,
                              style: const TextStyle(
                                fontFamily: 'monospace',
                                color: Color(0xFFCDD6F4),
                                fontSize: 13,
                                height: 1.4,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildDiffView(String diff) {
    final diffLines = diff.split('\n');
    return SingleChildScrollView(
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: diffLines.map((line) {
          Color color = Colors.white;
          if (line.startsWith('+')) {
            color = Colors.greenAccent;
          } else if (line.startsWith('-')) {
            color = Colors.redAccent;
          } else if (line.startsWith('@@')) {
            color = Colors.cyanAccent;
          }
          return Text(
            line,
            style: TextStyle(
              fontFamily: 'monospace',
              color: color,
              fontSize: 12,
            ),
          );
        }).toList(),
      ),
    );
  }
}
