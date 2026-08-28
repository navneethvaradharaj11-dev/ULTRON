import 'package:flutter/material.dart';
import '../models/code_models.dart';

class CodeFileTree extends StatelessWidget {
  final List<CodeFile> files;
  final CodeFile? activeFile;
  final ValueChanged<CodeFile> onFileSelected;

  const CodeFileTree({
    super.key,
    required this.files,
    required this.activeFile,
    required this.onFileSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF181825),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.all(12),
            child: Row(
              children: [
                Icon(Icons.folder, color: Colors.amberAccent, size: 18),
                SizedBox(width: 8),
                Text(
                  'FILESYSTEM WORKSPACE',
                  style: TextStyle(
                    color: Colors.amberAccent,
                    fontWeight: FontWeight.bold,
                    fontSize: 11,
                    letterSpacing: 1.0,
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: Colors.white10),
          Expanded(
            child: Material(
              color: Colors.transparent,
              child: ListView.builder(
                itemCount: files.length,
                itemBuilder: (context, index) {
                  final file = files[index];
                  final isSelected = activeFile?.id == file.id;

                  return ListTile(
                    dense: true,
                    selected: isSelected,
                    selectedTileColor: Colors.cyanAccent.withValues(alpha: 0.15),
                    leading: Icon(
                      _getFileIcon(file.language),
                      color: isSelected ? Colors.cyanAccent : Colors.white70,
                      size: 16,
                    ),
                    title: Text(
                      file.path,
                      style: TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 12,
                        color: isSelected ? Colors.cyanAccent : Colors.white,
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                    onTap: () => onFileSelected(file),
                  );
                },
              ),
            ),
          ),

        ],
      ),
    );
  }

  IconData _getFileIcon(String language) {
    switch (language.toLowerCase()) {
      case 'python':
      case 'py':
        return Icons.code;
      case 'c':
      case 'cpp':
      case 'c++':
        return Icons.memory;
      case 'javascript':
      case 'js':
        return Icons.javascript;
      default:
        return Icons.insert_drive_file;
    }
  }
}
