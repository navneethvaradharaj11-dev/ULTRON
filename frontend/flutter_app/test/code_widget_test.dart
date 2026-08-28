import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_app/models/code_models.dart';
import 'package:flutter_app/widgets/code_editor.dart';
import 'package:flutter_app/widgets/code_file_tree.dart';
import 'package:flutter_app/widgets/code_output_panel.dart';


void main() {
  testWidgets('CodeEditor renders filename, language, and content', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: CodeEditor(
            filename: 'main.py',
            content: 'print("Hello ULTRON")',
            language: 'python',
          ),
        ),
      ),
    );

    expect(find.text('main.py'), findsOneWidget);
    expect(find.text('PYTHON'), findsOneWidget);
    expect(find.text('print("Hello ULTRON")'), findsOneWidget);
  });

  testWidgets('CodeFileTree renders file items', (WidgetTester tester) async {
    final file = CodeFile(id: 'f1', path: 'factorial.py', language: 'python', content: '');
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: CodeFileTree(
            files: [file],
            activeFile: file,
            onFileSelected: (f) {},
          ),
        ),
      ),
    );

    expect(find.text('factorial.py'), findsOneWidget);
  });

  testWidgets('CodeOutputPanel displays stdout and stderr', (WidgetTester tester) async {
    final exec = CodeExecution(
      id: 'e1',
      workspaceId: 'w1',
      executionId: 'ex1',
      language: 'python',
      status: 'COMPLETED',
      stdout: 'Result: 120',
      stderr: '',
      durationMs: 15,
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: CodeOutputPanel(execution: exec),
        ),
      ),
    );

    expect(find.text('Result: 120'), findsOneWidget);
  });
}
