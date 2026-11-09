import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/learning_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/learning_event_card.dart';

class LearningDashboardScreen extends StatefulWidget {
  static const routeName = '/learning-dashboard';

  const LearningDashboardScreen({super.key});

  @override
  State<LearningDashboardScreen> createState() => _LearningDashboardScreenState();
}

class _LearningDashboardScreenState extends State<LearningDashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final token = Provider.of<AuthProvider>(context, listen: false).token;
      if (token != null) {
        final lp = Provider.of<LearningProvider>(context, listen: false);
        lp.fetchLearningEvents(token);
        lp.fetchStrategies(token);
        lp.fetchAgentMetrics(token);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final lp = Provider.of<LearningProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Adaptive Learning Timeline'),
      ),
      body: lp.isLoading
          ? const Center(child: CircularProgressIndicator())
          : lp.events.isEmpty
              ? const Center(child: Text('No learning events recorded yet.'))
              : ListView.builder(
                  itemCount: lp.events.length,
                  itemBuilder: (ctx, i) {
                    return LearningEventCard(event: lp.events[i]);
                  },
                ),
    );
  }
}
