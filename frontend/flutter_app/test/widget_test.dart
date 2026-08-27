import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_app/main.dart';

void main() {
  testWidgets('ULTRON App smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const UltronApp());
    expect(find.text('ULTRON'), findsOneWidget);
  });
}
