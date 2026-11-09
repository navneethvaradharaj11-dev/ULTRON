// ignore_for_file: avoid_print
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_app/providers/auth_provider.dart';
import 'package:flutter_app/providers/ultron_provider.dart';
import 'package:flutter_app/providers/workflow_provider.dart';
import 'package:flutter_app/providers/autonomy_provider.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('ULTRON Live Tailscale Network & Mobile API Tests', () {
    final String testUser = 'm_user_${DateTime.now().millisecondsSinceEpoch}';
    final String testEmail = '$testUser@ultron.internal';
    const String testPass = 'MobileSecurePass123!';
    String? jwtToken;

    test('1. Mobile Register & Login through Tailscale Portproxy', () async {
      final auth = AuthProvider();

      // Register new mobile user
      final regSuccess = await auth.register(testUser, testEmail, testPass);
      expect(regSuccess, isTrue);

      // Login mobile user
      final loginSuccess = await auth.login(testUser, testPass);
      expect(loginSuccess, isTrue);
      expect(auth.isAuthenticated, isTrue);
      expect(auth.token, isNotNull);
      expect(auth.token!.isNotEmpty, isTrue);

      jwtToken = auth.token;
      print('Mobile Auth Verified! Token: ${jwtToken!.substring(0, 15)}...');
    });

    test('2. Real API Requests: System Status & All 16 Capabilities', () async {
      expect(jwtToken, isNotNull);
      final ultron = UltronProvider();
      await ultron.fetchStatus(jwtToken!);

      expect(ultron.error, isNull);
      expect(ultron.status, isNotNull);
      expect(ultron.status!.systemStatus, equals('HEALTHY'));
      expect(ultron.status!.totalCapabilities, equals(16));
      expect(ultron.status!.availableCapabilities, equals(16));
      print('Live Capabilities Verified: 16/16 available');
    });

    test('3. Real Workflow & Autonomy Endpoints over Tailscale', () async {
      expect(jwtToken, isNotNull);

      // Workflow fetch
      final wfProvider = WorkflowProvider();
      await wfProvider.fetchWorkflows(jwtToken!);
      expect(wfProvider.error, isNull);

      // Autonomy rules fetch
      final autoProvider = AutonomyProvider();
      await autoProvider.fetchRules(jwtToken!);
      expect(autoProvider.error, isNull);
      print('Live Workflows & Autonomy Endpoints Verified!');
    });

    test('4. Real AI Command Interaction from Mobile Client', () async {
      expect(jwtToken, isNotNull);
      final ultron = UltronProvider();

      final cmdResult = await ultron.sendCommand(jwtToken!, 'What is the current system status?');
      expect(cmdResult, isNotNull);
      expect(cmdResult!['status'], anyOf(equals('COMPLETED'), equals('SUCCESS'), equals('QUEUED'), equals('RUNNING'), equals('healthy')));
      print('Live AI Interaction Result: $cmdResult');
    });
  });
}
