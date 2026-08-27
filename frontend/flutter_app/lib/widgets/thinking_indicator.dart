import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import '../core/theme/ultron_theme.dart';

class ThinkingIndicator extends StatelessWidget {
  final String agentName;
  final String detail;

  const ThinkingIndicator({
    Key? key,
    required this.agentName,
    required this.detail,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: UltronTheme.primaryNeon.withOpacity(0.4)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const SpinKitPulse(color: UltronTheme.primaryNeon, size: 18),
          const SizedBox(width: 10),
          Text(
            '[$agentName] ',
            style: const TextStyle(
              color: UltronTheme.primaryNeon,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
          Flexible(
            child: Text(
              detail.isEmpty ? 'Processing...' : detail,
              style: const TextStyle(color: UltronTheme.textMuted, fontSize: 12),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}
