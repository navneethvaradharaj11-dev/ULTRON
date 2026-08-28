import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/ultron_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/ultron_provider.dart';

class UltronCommandCenter extends StatefulWidget {
  const UltronCommandCenter({Key? key}) : super(key: key);

  @override
  State<UltronCommandCenter> createState() => _UltronCommandCenterState();
}

class _UltronCommandCenterState extends State<UltronCommandCenter> {
  final TextEditingController _commandController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      final ultron = Provider.of<UltronProvider>(context, listen: false);
      if (auth.token != null) {
        ultron.fetchStatus(auth.token!);
        ultron.fetchTimeline(auth.token!);
      }
    });
  }

  void _submitCommand() {
    final text = _commandController.text.trim();
    if (text.isEmpty) return;
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final ultron = Provider.of<UltronProvider>(context, listen: false);
    if (auth.token != null) {
      ultron.sendCommand(auth.token!, text);
      _commandController.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    final ultron = Provider.of<UltronProvider>(context);

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Unified Command Input Card
            Card(
              color: UltronTheme.cardBg,
              child: Padding(
                padding: const EdgeInsets.all(14.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.psychology, color: UltronTheme.primaryNeon, size: 24.0),
                        SizedBox(width: 8.0),
                        Text('What should ULTRON handle for you?', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0)),
                      ],
                    ),
                    const SizedBox(height: 10.0),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _commandController,
                            decoration: const InputDecoration(
                              hintText: 'Type goal or voice command...',
                              border: OutlineInputBorder(),
                              isDense: true,
                            ),
                            onSubmitted: (_) => _submitCommand(),
                          ),
                        ),
                        const SizedBox(width: 8.0),
                        IconButton(
                          icon: const Icon(Icons.send, color: UltronTheme.primaryNeon),
                          onPressed: _submitCommand,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12.0),
            // System Capabilities Health Header
            if (ultron.status != null)
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('System: ${ultron.status!.operatingSystem}', style: const TextStyle(fontSize: 12.0, color: UltronTheme.textMuted)),
                  Text('Capabilities: ${ultron.status!.availableCapabilities}/${ultron.status!.totalCapabilities} ACTIVE', style: const TextStyle(fontSize: 12.0, color: UltronTheme.primaryNeon, fontWeight: FontWeight.bold)),
                ],
              ),
            const SizedBox(height: 10.0),
            const Text('Unified Activity Stream', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0)),
            const SizedBox(height: 6.0),
            Expanded(
              child: ultron.activities.isEmpty
                  ? const Center(child: Text('No system activity recorded yet.', style: TextStyle(color: UltronTheme.textMuted)))
                  : ListView.builder(
                      itemCount: ultron.activities.length,
                      itemBuilder: (context, index) {
                        final act = ultron.activities[index];
                        return Card(
                          color: UltronTheme.cardBg,
                          margin: const EdgeInsets.symmetric(vertical: 4.0),
                          child: ListTile(
                            leading: const Icon(Icons.bolt, color: UltronTheme.primaryNeon),
                            title: Text(act.title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13.0)),
                            subtitle: Text(act.details ?? act.activityType),
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
