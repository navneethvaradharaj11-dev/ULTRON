import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/code_provider.dart';
import '../../widgets/code_editor.dart';
import '../../widgets/code_file_tree.dart';
import '../../widgets/code_output_panel.dart';
import '../../widgets/code_execution_timeline.dart';
import '../../widgets/code_test_result.dart';
import '../../widgets/code_artifact_card.dart';

class CodeScreen extends StatefulWidget {
  const CodeScreen({super.key});

  @override
  State<CodeScreen> createState() => _CodeScreenState();
}

class _CodeScreenState extends State<CodeScreen> {
  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<CodeProvider>(context);
    final activeFile = provider.activeFile;

    return Scaffold(
      backgroundColor: const Color(0xFF11111B),
      appBar: AppBar(
        backgroundColor: const Color(0xFF181825),
        title: const Row(
          children: [
            Icon(Icons.terminal, color: Colors.cyanAccent),
            SizedBox(width: 8),
            Text(
              'ULTRON CODE INTELLIGENCE',
              style: TextStyle(
                color: Colors.cyanAccent,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.2,
                fontSize: 16,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.play_arrow, color: Colors.greenAccent),
            tooltip: 'Run Sandbox Execution',
            onPressed: () {
              // Trigger execution monitor
            },
          ),
          IconButton(
            icon: const Icon(Icons.bug_report, color: Colors.amberAccent),
            tooltip: 'Run Test Suite',
            onPressed: () {},
          ),
        ],
      ),
      body: Row(
        children: [
          // Sidebar: Workspace File Tree (250px)
          SizedBox(
            width: 250,
            child: CodeFileTree(
              files: provider.activeWorkspace?.files ?? [],
              activeFile: activeFile,
              onFileSelected: (file) => provider.setActiveFile(file),
            ),
          ),
          const VerticalDivider(width: 1, color: Colors.white10),

          // Main Code Editor & Output Dashboard
          Expanded(
            child: Column(
              children: [
                // Code Editor Workspace
                Expanded(
                  flex: 3,
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: CodeEditor(
                      filename: activeFile?.path ?? 'No file selected',
                      content: activeFile?.content ?? '// Select a file from the workspace to begin.',
                      language: activeFile?.language ?? 'text',
                      diffText: provider.diffText,
                    ),
                  ),
                ),

                // Console Output & Test / Timeline Panel (Bottom 2 Flex)
                Expanded(
                  flex: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Row(
                      children: [
                        Expanded(
                          flex: 3,
                          child: CodeOutputPanel(execution: provider.currentExecution),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          flex: 2,
                          child: CodeExecutionTimeline(events: provider.timelineEvents),
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
    );
  }
}
