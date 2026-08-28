import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/ultron_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/workflow_provider.dart';
import '../../widgets/task_graph_visualization.dart';
import '../../widgets/approval_request_card.dart';
import '../../widgets/agent_status_grid.dart';
import '../../widgets/workflow_event_timeline.dart';
import '../../widgets/workflow_result_card.dart';

class WorkflowDetailScreen extends StatefulWidget {
  final String workflowId;

  const WorkflowDetailScreen({Key? key, required this.workflowId}) : super(key: key);

  @override
  State<WorkflowDetailScreen> createState() => _WorkflowDetailScreenState();
}

class _WorkflowDetailScreenState extends State<WorkflowDetailScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      final wf = Provider.of<WorkflowProvider>(context, listen: false);
      if (auth.token != null) {
        wf.fetchWorkflowDetail(auth.token!, widget.workflowId);
        wf.connectRealtimeStream(widget.workflowId, auth.token!);
      }
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final wfProv = Provider.of<WorkflowProvider>(context);
    final auth = Provider.of<AuthProvider>(context);
    final wf = wfProv.activeWorkflow;
    final token = auth.token ?? '';

    return Scaffold(
      appBar: AppBar(
        title: Text(wf != null ? 'Workflow: ${wf.goal}' : 'Remote Control'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'DAG GRAPH'),
            Tab(text: 'CONTROL'),
            Tab(text: 'TIMELINE'),
            Tab(text: 'RESULTS'),
          ],
        ),
      ),
      body: Column(
        children: [
          // Notification Toast Banner
          if (wfProv.notifications.isNotEmpty)
            Container(
              color: UltronTheme.accentCyan.withValues(alpha: 0.2),
              padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 6.0),
              child: Row(
                children: [
                  const Icon(Icons.notifications_active, color: UltronTheme.primaryNeon, size: 16),
                  const SizedBox(width: 8.0),
                  Expanded(
                    child: Text(
                      wfProv.notifications.first,
                      style: const TextStyle(fontSize: 12.0, fontWeight: FontWeight.bold),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, size: 14),
                    onPressed: () => wfProv.clearNotifications(),
                  ),
                ],
              ),
            ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                // 1. DAG Graph Tab
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: TaskGraphVisualization(steps: wfProv.activeSteps),
                ),
                // 2. Control & Agent Status Tab
                SingleChildScrollView(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Workflow Overview Header
                      Card(
                        color: UltronTheme.cardBg,
                        child: Padding(
                          padding: const EdgeInsets.all(12.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Goal: ${wf?.goal ?? ''}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15.0)),
                              const SizedBox(height: 6.0),
                              Text('Status: ${wf?.state ?? ''} • Progress: ${((wf?.progress ?? 0.0) * 100).toInt()}%'),
                              const SizedBox(height: 8.0),
                              LinearProgressIndicator(value: wf?.progress ?? 0.0, color: UltronTheme.accentCyan),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 12.0),
                      // Server-Side Remote Control Action Buttons
                      const Text('Server-Side Remote Controls', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0)),
                      const SizedBox(height: 8.0),
                      Row(
                        children: [
                          ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(backgroundColor: UltronTheme.success, foregroundColor: Colors.white),
                            icon: const Icon(Icons.play_arrow),
                            label: const Text('START'),
                            onPressed: () => wfProv.startWorkflow(token, widget.workflowId),
                          ),
                          const SizedBox(width: 6.0),
                          ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(backgroundColor: UltronTheme.warning, foregroundColor: Colors.black),
                            icon: const Icon(Icons.pause),
                            label: const Text('PAUSE'),
                            onPressed: () => wfProv.pauseWorkflow(token, widget.workflowId),
                          ),
                          const SizedBox(width: 6.0),
                          ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(backgroundColor: UltronTheme.accentCyan, foregroundColor: Colors.black),
                            icon: const Icon(Icons.play_circle_outline),
                            label: const Text('RESUME'),
                            onPressed: () => wfProv.resumeWorkflow(token, widget.workflowId),
                          ),
                          const SizedBox(width: 6.0),
                          OutlinedButton.icon(
                            style: OutlinedButton.styleFrom(foregroundColor: UltronTheme.error),
                            icon: const Icon(Icons.cancel),
                            label: const Text('CANCEL'),
                            onPressed: () => wfProv.cancelWorkflow(token, widget.workflowId),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16.0),
                      // Pending Approvals Section
                      const Text('Pending Approvals', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0)),
                      const SizedBox(height: 6.0),
                      if (wfProv.activeApprovals.isEmpty)
                        const Text('No pending approval requests.', style: TextStyle(color: UltronTheme.textMuted, fontSize: 12.0))
                      else
                        ...wfProv.activeApprovals.map(
                          (appr) => ApprovalRequestCard(
                            approval: appr,
                            onDecision: (approved) {
                              wfProv.approveDecision(token, widget.workflowId, appr.id, approved);
                            },
                          ),
                        ),
                      const SizedBox(height: 16.0),
                      // Active Agent Status Grid
                      const Text('Specialist Agent Team Matrix', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0)),
                      const SizedBox(height: 8.0),
                      AgentStatusGrid(activeAgent: wf?.currentStep ?? 'commander'),
                    ],
                  ),
                ),
                // 3. Timeline Tab
                Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: WorkflowEventTimeline(events: wfProv.activeEvents),
                ),
                // 4. Results & Artifacts Tab
                SingleChildScrollView(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (wfProv.activeResult != null) WorkflowResultCard(result: wfProv.activeResult!),
                      const SizedBox(height: 12.0),
                      const Text('Generated Artifacts', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14.0)),
                      if (wfProv.activeArtifacts.isEmpty)
                        const Text('No artifacts generated yet.', style: TextStyle(color: UltronTheme.textMuted, fontSize: 12.0))
                      else
                        ...wfProv.activeArtifacts.map(
                          (art) => Card(
                            color: UltronTheme.cardBg,
                            child: ListTile(
                              leading: const Icon(Icons.insert_drive_file, color: UltronTheme.accentCyan),
                              title: Text(art.filename),
                              subtitle: Text('Size: ${art.sizeBytes} bytes • Type: ${art.artifactType}'),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
