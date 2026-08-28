import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/computer_provider.dart';
import '../../widgets/screenshot_view.dart';
import '../../widgets/computer_timeline.dart';
import '../../widgets/approval_dialog.dart';

class ComputerSessionScreen extends StatelessWidget {
  const ComputerSessionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<ComputerProvider>(context);
    final pending = provider.pendingApprovalAction;

    return Scaffold(
      backgroundColor: const Color(0xFF11111B),
      appBar: AppBar(
        backgroundColor: const Color(0xFF181825),
        title: const Text(
          'CONTROLLED COMPUTER INTERACTION',
          style: TextStyle(
            color: Colors.cyanAccent,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.2,
            fontSize: 16,
          ),
        ),
      ),
      body: Stack(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(
                  flex: 3,
                  child: ScreenshotViewWidget(
                    screenshotId: provider.activeSessionId ?? 'session_shot',
                    width: provider.viewportWidth,
                    height: provider.viewportHeight,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  flex: 2,
                  child: ComputerTimelineWidget(actions: provider.actionHistory),
                ),
              ],
            ),
          ),
          if (pending != null)
            ApprovalDialogWidget(
              action: pending,
              onApprove: () => provider.clearPendingApproval(),
              onReject: () => provider.clearPendingApproval(),
            ),
        ],
      ),
    );
  }
}
