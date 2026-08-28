import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_app/models/perception_models.dart';
import 'package:flutter_app/widgets/perception_element_card.dart';
import 'package:flutter_app/widgets/computer_action_card.dart';
import 'package:flutter_app/widgets/confidence_indicator.dart';

void main() {
  testWidgets('PerceptionElementCard renders label and type', (WidgetTester tester) async {
    final elem = PerceptionElement(
      id: 'btn_1',
      type: 'button',
      label: 'Submit Order',
      bbox: {'x': 10, 'y': 20, 'width': 100, 'height': 40},
      confidence: 0.95,
      interactive: true,
      sensitive: true,
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: PerceptionElementCard(element: elem),
        ),
      ),
    );

    expect(find.text('Submit Order'), findsOneWidget);
    expect(find.text('SENSITIVE'), findsOneWidget);
  });

  testWidgets('ComputerActionCard renders action type and status', (WidgetTester tester) async {
    final action = ComputerActionItem(
      actionId: 'act_1',
      sessionId: 'sess_1',
      actionType: 'CLICK',
      status: 'COMPLETED',
      approvalState: 'AUTO_APPROVED',
      confidence: 0.98,
      timestamp: '2026-08-28T12:00:00Z',
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: ComputerActionCard(action: action),
        ),
      ),
    );

    expect(find.text('ACTION: CLICK'), findsOneWidget);
    expect(find.text('STATUS: COMPLETED • APPROVAL: AUTO_APPROVED'), findsOneWidget);
  });

  testWidgets('ConfidenceIndicatorWidget renders confidence percentage', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: ConfidenceIndicatorWidget(confidence: 0.92),
        ),
      ),
    );

    expect(find.text('PERCEIVED CONFIDENCE: 92%'), findsOneWidget);
  });
}
