import 'package:flutter/material.dart';

class BrowserView extends StatelessWidget {
  final String url;
  final String title;
  final String pageText;
  final List<dynamic> elements;

  const BrowserView({
    Key? key,
    required this.url,
    required this.title,
    required this.pageText,
    this.elements = const [],
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E2E),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.cyanAccent.withOpacity(0.3)),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // URL Bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.black45,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                const Icon(Icons.language, color: Colors.cyanAccent, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    url.isEmpty ? 'about:blank' : url,
                    style: const TextStyle(color: Colors.white, fontFamily: 'monospace', fontSize: 13),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Text(
            title.isEmpty ? 'Untitled Page' : title,
            style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const Divider(color: Colors.white24, height: 24),
          Expanded(
            child: SingleChildScrollView(
              child: Text(
                pageText.isEmpty ? 'No page content loaded.' : pageText,
                style: const TextStyle(color: Colors.white70, fontSize: 14, height: 1.5),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
