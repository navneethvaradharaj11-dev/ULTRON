import 'package:flutter/material.dart';
import '../core/theme/ultron_theme.dart';

class AgentStatusGrid extends StatelessWidget {
  final String activeAgent;

  const AgentStatusGrid({super.key, required this.activeAgent});

  static const List<String> _agents = [
    'commander',
    'planner',
    'researcher',
    'coder',
    'reviewer',
    'browser',
    'computer',
    'learning',
  ];

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 4,
        childAspectRatio: 2.2,
        crossAxisSpacing: 6,
        mainAxisSpacing: 6,
      ),
      itemCount: _agents.length,
      itemBuilder: (context, index) {
        final agent = _agents[index];
        final isActive = agent.toLowerCase() == activeAgent.toLowerCase();
        final color = isActive ? UltronTheme.primaryNeon : UltronTheme.textMuted;

        return Container(
          decoration: BoxDecoration(
            color: isActive ? UltronTheme.primaryNeon.withValues(alpha: 0.15) : UltronTheme.cardBg,
            borderRadius: BorderRadius.circular(6.0),
            border: Border.all(color: color, width: isActive ? 1.5 : 0.5),
          ),
          padding: const EdgeInsets.all(6.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                agent.toUpperCase(),
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.bold,
                  fontSize: 10.0,
                ),
              ),
              Text(
                isActive ? 'ACTIVE' : 'IDLE',
                style: TextStyle(
                  color: isActive ? UltronTheme.success : Colors.grey,
                  fontSize: 9.0,
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
