import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/learning_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/strategy_card.dart';

class StrategyScreen extends StatefulWidget {
  static const routeName = '/strategy-library';

  const StrategyScreen({super.key});

  @override
  State<StrategyScreen> createState() => _StrategyScreenState();
}

class _StrategyScreenState extends State<StrategyScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final token = Provider.of<AuthProvider>(context, listen: false).token;
      if (token != null) {
        Provider.of<LearningProvider>(context, listen: false).fetchStrategies(token);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final lp = Provider.of<LearningProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Strategy Library'),
      ),
      body: lp.strategies.isEmpty
          ? const Center(child: Text('No strategies learned yet.'))
          : ListView.builder(
              itemCount: lp.strategies.length,
              itemBuilder: (ctx, i) {
                return StrategyCard(strategy: lp.strategies[i]);
              },
            ),
    );
  }
}
