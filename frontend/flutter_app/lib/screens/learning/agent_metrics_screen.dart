import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/learning_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/agent_metric_card.dart';

class AgentMetricsScreen extends StatefulWidget {
  static const routeName = '/agent-metrics';

  const AgentMetricsScreen({super.key});

  @override
  State<AgentMetricsScreen> createState() => _AgentMetricsScreenState();
}

class _AgentMetricsScreenState extends State<AgentMetricsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final token = Provider.of<AuthProvider>(context, listen: false).token;
      if (token != null) {
        Provider.of<LearningProvider>(context, listen: false).fetchAgentMetrics(token);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final lp = Provider.of<LearningProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Agent Performance Metrics'),
      ),
      body: lp.metrics.isEmpty
          ? const Center(child: Text('No agent metrics available.'))
          : ListView.builder(
              itemCount: lp.metrics.length,
              itemBuilder: (ctx, i) {
                return AgentMetricCard(metric: lp.metrics[i]);
              },
            ),
    );
  }
}
