import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/ultron_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/integration_provider.dart';

class IntegrationDashboard extends StatefulWidget {
  const IntegrationDashboard({super.key});

  @override
  State<IntegrationDashboard> createState() => _IntegrationDashboardState();
}

class _IntegrationDashboardState extends State<IntegrationDashboard> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      final provider = Provider.of<IntegrationProvider>(context, listen: false);
      if (auth.token != null) {
        provider.fetchIntegrations(auth.token!);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<IntegrationProvider>(context);
    final auth = Provider.of<AuthProvider>(context, listen: false);

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Universal Connector Fabric', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16.0)),
            const SizedBox(height: 4.0),
            const Text('Connect external services safely with scope policy governance.', style: TextStyle(fontSize: 12.0, color: UltronTheme.textMuted)),
            const SizedBox(height: 12.0),
            Expanded(
              child: provider.isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : provider.integrations.isEmpty
                      ? const Center(child: Text('No integrations available.', style: TextStyle(color: UltronTheme.textMuted)))
                      : ListView.builder(
                          itemCount: provider.integrations.length,
                          itemBuilder: (context, index) {
                            final item = provider.integrations[index];
                            return Card(
                              color: UltronTheme.cardBg,
                              margin: const EdgeInsets.symmetric(vertical: 4.0),
                              child: ListTile(
                                leading: Icon(
                                  item.id == 'github'
                                      ? Icons.code
                                      : item.id == 'calendar'
                                          ? Icons.calendar_month
                                          : item.id == 'email'
                                              ? Icons.email
                                              : Icons.folder,
                                  color: UltronTheme.primaryNeon,
                                ),
                                title: Text(item.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0)),
                                subtitle: Text('${item.description}\nHealth: ${item.healthStatus}', style: const TextStyle(fontSize: 11.0)),
                                isThreeLine: true,
                                trailing: ElevatedButton(
                                  onPressed: () {
                                    if (auth.token != null) {
                                      if (item.isConnected) {
                                        provider.disconnectIntegration(auth.token!, item.id);
                                      } else {
                                        provider.connectIntegration(auth.token!, item.id);
                                      }
                                    }
                                  },
                                  child: Text(item.isConnected ? 'Disconnect' : 'Connect', style: const TextStyle(fontSize: 11.0)),
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
