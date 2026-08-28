import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/ultron_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/autonomy_provider.dart';

class AutonomyDashboard extends StatefulWidget {
  const AutonomyDashboard({Key? key}) : super(key: key);

  @override
  State<AutonomyDashboard> createState() => _AutonomyDashboardState();
}

class _AutonomyDashboardState extends State<AutonomyDashboard> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      final auto = Provider.of<AutonomyProvider>(context, listen: false);
      if (auth.token != null) {
        auto.fetchRules(auth.token!);
        auto.fetchNotifications(auth.token!);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final auto = Provider.of<AutonomyProvider>(context);
    final auth = Provider.of<AuthProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Proactive Autonomy Engine'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              if (auth.token != null) {
                auto.fetchRules(auth.token!);
                auto.fetchNotifications(auth.token!);
              }
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status Card
            Card(
              color: UltronTheme.cardBg,
              child: Padding(
                padding: const EdgeInsets.all(12.0),
                child: Row(
                  children: [
                    const Icon(Icons.bolt, color: UltronTheme.primaryNeon, size: 28.0),
                    const SizedBox(width: 10.0),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Engine Status: ACTIVE', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0)),
                        Text('Active Rules: ${auto.rules.where((r) => r.enabled).length} • Notifications: ${auto.notifications.length}', style: const TextStyle(color: UltronTheme.textMuted, fontSize: 12.0)),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12.0),
            // Proactive Rules Section
            const Text('Autonomous Rules', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0)),
            const SizedBox(height: 6.0),
            Expanded(
              child: auto.rules.isEmpty
                  ? const Center(child: Text('No autonomous rules created yet.', style: TextStyle(color: UltronTheme.textMuted)))
                  : ListView.builder(
                      itemCount: auto.rules.length,
                      itemBuilder: (context, index) {
                        final rule = auto.rules[index];
                        return Card(
                          color: UltronTheme.cardBg,
                          margin: const EdgeInsets.symmetric(vertical: 4.0),
                          child: ListTile(
                            leading: Icon(
                              rule.enabled ? Icons.check_circle : Icons.pause_circle_outline,
                              color: rule.enabled ? UltronTheme.primaryNeon : UltronTheme.textMuted,
                            ),
                            title: Text(rule.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0)),
                            subtitle: Text('Trigger: ${rule.triggerType} • Level: ${rule.autonomyLevel}'),
                            trailing: Switch(
                              value: rule.enabled,
                              activeColor: UltronTheme.primaryNeon,
                              onChanged: (val) {
                                if (auth.token != null) {
                                  auto.toggleRule(auth.token!, rule.ruleId, val);
                                }
                              },
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
