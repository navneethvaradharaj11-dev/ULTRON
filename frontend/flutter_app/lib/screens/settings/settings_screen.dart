import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/ultron_theme.dart';
import '../../providers/auth_provider.dart';
import '../../services/api_service.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    return Scaffold(
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: ListTile(
              leading: const Icon(Icons.person, color: UltronTheme.primaryNeon),
              title: Text(auth.user?.username ?? 'ULTRON User', style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text(auth.user?.email ?? 'user@ultron.ai'),
            ),
          ),
          const SizedBox(height: 16),
          const Text('NETWORK & TAILSCALE GATEWAY', style: TextStyle(color: UltronTheme.accentCyan, fontWeight: FontWeight.bold, fontSize: 12)),
          const SizedBox(height: 8),
          Card(
            child: ListTile(
              leading: const Icon(Icons.lan, color: UltronTheme.accentCyan),
              title: const Text('Gateway API Endpoint'),
              subtitle: Text(ApiService.baseUrl),
              trailing: const Icon(Icons.check_circle, color: UltronTheme.success, size: 20),
            ),
          ),
          const SizedBox(height: 16),
          const Text('AI PROVIDER CONFIGURATION', style: TextStyle(color: UltronTheme.accentCyan, fontWeight: FontWeight.bold, fontSize: 12)),
          const SizedBox(height: 8),
          const Card(
            child: ListTile(
              leading: Icon(Icons.smart_toy, color: UltronTheme.primaryNeon),
              title: Text('Active AI Provider'),
              subtitle: Text('Google Gemini / OpenAI / Mock Provider'),
            ),
          ),
          const SizedBox(height: 16),
          const Text('SECURITY & PERMISSIONS', style: TextStyle(color: UltronTheme.accentCyan, fontWeight: FontWeight.bold, fontSize: 12)),
          const SizedBox(height: 8),
          const Card(
            child: ListTile(
              leading: Icon(Icons.security, color: UltronTheme.success),
              title: Text('Tool Permission Boundaries'),
              subtitle: Text('Filesystem Write & Shell Execution Require Approval'),
            ),
          ),
        ],
      ),
    );
  }
}
