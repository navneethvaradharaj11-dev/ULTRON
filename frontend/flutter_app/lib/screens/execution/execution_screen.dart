import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/ultron_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/execution_provider.dart';
import 'execution_detail_screen.dart';

/// Primary Execution tab: goal submission + execution history list
class ExecutionScreen extends StatefulWidget {
  const ExecutionScreen({Key? key}) : super(key: key);

  @override
  State<ExecutionScreen> createState() => _ExecutionScreenState();
}

class _ExecutionScreenState extends State<ExecutionScreen>
    with SingleTickerProviderStateMixin {
  final _goalController = TextEditingController();
  late final TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      final exec = Provider.of<ExecutionProvider>(context, listen: false);
      if (auth.token != null) {
        exec.fetchExecutions(auth.token!);
        exec.fetchAgentMetrics(auth.token!);
      }
    });
  }

  @override
  void dispose() {
    _goalController.dispose();
    _tabController.dispose();
    super.dispose();
  }

  void _startExecution() {
    final goal = _goalController.text.trim();
    if (goal.isEmpty) return;
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final exec = Provider.of<ExecutionProvider>(context, listen: false);
    if (auth.token != null) {
      exec.startGoalExecution(auth.token!, goal);
      _goalController.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          _buildGoalInput(),
          _buildTabBar(),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _ExecutionHistoryTab(),
                _AgentMetricsTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGoalInput() {
    return Container(
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 8),
      decoration: BoxDecoration(
        color: const Color(0xFF0F1B2D),
        border: Border(bottom: BorderSide(color: UltronTheme.primaryNeon.withOpacity(0.2))),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'AGENTIC GOAL EXECUTION',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              letterSpacing: 1.4,
              fontSize: 11,
              color: UltronTheme.primaryNeon,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _goalController,
                  decoration: const InputDecoration(
                    hintText: 'Enter autonomous goal…',
                    prefixIcon: Icon(Icons.bolt_outlined, size: 18),
                    isDense: true,
                  ),
                  onSubmitted: (_) => _startExecution(),
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton.icon(
                icon: const Icon(Icons.play_arrow, size: 16),
                label: const Text('EXECUTE'),
                onPressed: _startExecution,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTabBar() {
    return Container(
      color: const Color(0xFF0A1628),
      child: TabBar(
        controller: _tabController,
        indicatorColor: UltronTheme.primaryNeon,
        labelColor: UltronTheme.primaryNeon,
        unselectedLabelColor: UltronTheme.textMuted,
        labelStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 1),
        tabs: const [
          Tab(icon: Icon(Icons.history, size: 16), text: 'HISTORY'),
          Tab(icon: Icon(Icons.analytics_outlined, size: 16), text: 'METRICS'),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Execution History Tab
// ---------------------------------------------------------------------------

class _ExecutionHistoryTab extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final exec = Provider.of<ExecutionProvider>(context);

    if (exec.isLoading && exec.executions.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (exec.executions.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.account_tree_outlined, size: 48, color: UltronTheme.textMuted),
            const SizedBox(height: 12),
            Text('No executions yet', style: TextStyle(color: UltronTheme.textMuted)),
            const SizedBox(height: 6),
            Text('Submit a goal above to start', style: TextStyle(color: UltronTheme.textMuted, fontSize: 12)),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () async {
        if (auth.token != null) await exec.fetchExecutions(auth.token!);
      },
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        itemCount: exec.executions.length,
        itemBuilder: (context, index) {
          final e = exec.executions[index];
          return _ExecutionCard(
            item: e,
            token: auth.token ?? '',
          );
        },
      ),
    );
  }
}

class _ExecutionCard extends StatelessWidget {
  final ExecutionItem item;
  final String token;

  const _ExecutionCard({required this.item, required this.token});

  Color _statusColor(String status) {
    return switch (status) {
      'COMPLETED' => const Color(0xFF00FFA3),
      'FAILED'    => const Color(0xFFFF4D4D),
      'CANCELLED' => const Color(0xFFFF9900),
      'RUNNING'   => const Color(0xFF38BDF8),
      _           => const Color(0xFF64748B),
    };
  }

  IconData _statusIcon(String status) {
    return switch (status) {
      'COMPLETED' => Icons.check_circle_outline,
      'FAILED'    => Icons.error_outline,
      'CANCELLED' => Icons.cancel_outlined,
      'RUNNING'   => Icons.sync,
      _           => Icons.pending_outlined,
    };
  }

  @override
  Widget build(BuildContext context) {
    final exec = Provider.of<ExecutionProvider>(context, listen: false);
    final dateStr = item.createdAt.length >= 10 ? item.createdAt.substring(0, 10) : item.createdAt;

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: () {
          Navigator.of(context).push(MaterialPageRoute(
            builder: (_) => ExecutionDetailScreen(
              executionId: item.id,
              token: token,
            ),
          ));
        },
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(_statusIcon(item.status), color: _statusColor(item.status), size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      item.goal,
                      style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: _statusColor(item.status).withOpacity(0.12),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: _statusColor(item.status).withOpacity(0.5)),
                    ),
                    child: Text(
                      item.status,
                      style: TextStyle(color: _statusColor(item.status), fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Row(
                children: [
                  Icon(Icons.calendar_today_outlined, size: 12, color: UltronTheme.textMuted),
                  const SizedBox(width: 4),
                  Text(dateStr, style: TextStyle(color: UltronTheme.textMuted, fontSize: 11)),
                  if (item.tasks.isNotEmpty) ...[
                    const SizedBox(width: 12),
                    Icon(Icons.task_alt, size: 12, color: UltronTheme.textMuted),
                    const SizedBox(width: 4),
                    Text('${item.tasks.length} tasks', style: TextStyle(color: UltronTheme.textMuted, fontSize: 11)),
                  ],
                  const Spacer(),
                  // Action buttons
                  if (item.status == 'RUNNING' || item.status == 'PENDING') ...[
                    _ActionChip(
                      icon: Icons.stop_circle_outlined,
                      label: 'Cancel',
                      color: const Color(0xFFFF4D4D),
                      onTap: () => exec.cancelExecution(token, item.id),
                    ),
                  ],
                  if (item.status == 'RUNNING') ...[
                    const SizedBox(width: 6),
                    _ActionChip(
                      icon: Icons.refresh,
                      label: 'Resume',
                      color: const Color(0xFF38BDF8),
                      onTap: () => exec.resumeExecution(token, item.id),
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ActionChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionChip({required this.icon, required this.label, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: color.withOpacity(0.4)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 12, color: color),
            const SizedBox(width: 4),
            Text(label, style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Agent Metrics Tab
// ---------------------------------------------------------------------------

class _AgentMetricsTab extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final exec = Provider.of<ExecutionProvider>(context);
    final metrics = exec.agentMetrics;

    if (metrics.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.bar_chart, size: 48, color: UltronTheme.textMuted),
            const SizedBox(height: 12),
            Text('No agent metrics yet', style: TextStyle(color: UltronTheme.textMuted)),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: metrics.length,
      itemBuilder: (context, index) {
        final m = metrics[index];
        return _MetricsCard(metric: m);
      },
    );
  }
}

class _MetricsCard extends StatelessWidget {
  final AgentMetricItem metric;
  const _MetricsCard({required this.metric});

  @override
  Widget build(BuildContext context) {
    final successPct = (metric.successRate * 100).toStringAsFixed(1);
    final avgSec = metric.avgDurationSec.toStringAsFixed(2);

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.smart_toy_outlined, size: 18, color: UltronTheme.accentCyan),
                const SizedBox(width: 8),
                Text(
                  metric.agentName.toUpperCase(),
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: UltronTheme.accentCyan, letterSpacing: 0.8),
                ),
              ],
            ),
            const SizedBox(height: 10),
            // Success rate bar
            Row(
              children: [
                const Text('SUCCESS', style: TextStyle(fontSize: 10, color: Color(0xFF64748B))),
                const SizedBox(width: 8),
                Expanded(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: metric.successRate,
                      backgroundColor: const Color(0xFF1E293B),
                      valueColor: AlwaysStoppedAnimation(
                        metric.successRate >= 0.8
                            ? const Color(0xFF00FFA3)
                            : metric.successRate >= 0.5
                                ? const Color(0xFFFF9900)
                                : const Color(0xFFFF4D4D),
                      ),
                      minHeight: 8,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Text('$successPct%', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
              ],
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 16,
              runSpacing: 4,
              children: [
                _Stat(label: 'Tasks', value: '${metric.totalTasks}'),
                _Stat(label: 'OK', value: '${metric.completed}', color: const Color(0xFF00FFA3)),
                _Stat(label: 'Failed', value: '${metric.failed}', color: const Color(0xFFFF4D4D)),
                _Stat(label: 'Avg Time', value: '${avgSec}s'),
                _Stat(label: 'Retries', value: '${metric.totalRetries}'),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  final String label;
  final String value;
  final Color? color;

  const _Stat({required this.label, required this.value, this.color});

  @override
  Widget build(BuildContext context) {
    return RichText(
      text: TextSpan(
        children: [
          TextSpan(text: '$label: ', style: const TextStyle(color: Color(0xFF64748B), fontSize: 11)),
          TextSpan(text: value, style: TextStyle(color: color ?? Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
