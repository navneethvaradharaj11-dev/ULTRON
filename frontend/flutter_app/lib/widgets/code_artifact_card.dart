import 'package:flutter/material.dart';
import '../models/code_models.dart';

class CodeArtifactCard extends StatelessWidget {
  final CodeArtifact artifact;

  const CodeArtifactCard({
    super.key,
    required this.artifact,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: const Color(0xFF1E1E2E),
      margin: const EdgeInsets.symmetric(vertical: 4),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
        side: const BorderSide(color: Colors.amberAccent),
      ),
      child: Padding(
        padding: const EdgeInsets.all(10),
        child: Row(
          children: [
            const Icon(Icons.attachment, color: Colors.amberAccent, size: 20),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    artifact.filename,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                  Text(
                    '${artifact.mimeType} • ${artifact.sizeBytes} bytes',
                    style: const TextStyle(color: Colors.white54, fontSize: 10),
                  ),
                ],
              ),
            ),
            const Icon(Icons.download, color: Colors.amberAccent, size: 18),
          ],
        ),
      ),
    );
  }
}
