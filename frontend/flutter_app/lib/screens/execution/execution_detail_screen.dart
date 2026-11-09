import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/ultron_theme.dart';
import '../../providers/execution_provider.dart';
import '../../widgets/task_graph_widget.dart';

/// Detailed view for a single execution: task graph + event timeline + consistency badge
class ExecutionDetailScreen extends StatefulWidget {
  final String executionId;
  final String token;

  const ExecutionDetailScreen({
    super.key,
    required this.executionId,
    required this.token,
  });

  @override
  State<ExecutionDetailScreen> createState() => _ExecutionDetailScreenState();
}

class _ExecutionDetailScreenState extends State<ExecutionDetailScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;
  bool _isLoadingDetail = true;
  ExecutionDetail? _detail;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadDetail();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadDetail() async {
    setState(() {
      _isLoadingDetail = true;
      _error = null;
    });
    try {
      final exec = Provider.of<ExecutionProvider>(context, listen: false);
      final detail = await exec.fetchExecutionDetail(widget.token, widget.executionId);
      setState(() {
        _detail = detail;
        _isLoadingDetail = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoadingDetail = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Execution Detail', style: TextStyle(fontSize: 14, letterSpacing: 0.8)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, size: 20),
            onPressed: _loadDetail,
            tooltip: 'Refresh',
          ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(40),
          child: TabBar(
            controller: _tabController,
            indicatorColor: UltronTheme.primaryNeon,
            labelColor: UltronTheme.primaryNeon,
            unselectedLabelColor: UltronTheme.textMuted,
            labelStyle: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 0.8),
            tabs: const [
              Tab(text: 'TASKS'),
              Tab(text: 'EVENTS'),
              Tab(text: 'INFO'),
            ],
          ),
        ),
      ),
      body: _isLoadingDetail
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? _buildError()
              : _detail == null
                  ? const Center(child: Text('No detail available'))
                  : TabBarView(
                      controller: _tabController,
                      children: [
                        _TasksTab(detail: _detail!),
                        _EventsTab(detail: _detail!),
                        _InfoTab(detail: _detail!, token: widget.token),
                      ],
                    ),
    );
  }

  Widget _buildError() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 48, color: Color(0xFFFF4D4D)),
          const SizedBox(height: 12),
          Text(_error!, style: const TextStyle(color: Color(0xFFFF4D4D)), textAlign: TextAlign.center),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            icon: const Icon(Icons.refresh, size: 16),
            label: const Text('Retry'),
            onPressed: _loadDetail,
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Tasks Tab — task graph widget
// ---------------------------------------------------------------------------

class _TasksTab extends StatelessWidget {
  final ExecutionDetail detail;
  const _TasksTab({required this.detail});

  @override
  Widget build(BuildContext context) {
    if (detail.tasks.isEmpty) {
      return const Center(child: Text('No tasks found'));
    }
    return SingleChildScrollView(
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _SectionHeader(title: 'TASK GRAPH (${detail.tasks.length} tasks)'),
          const SizedBox(height: 10),
          TaskGraphWidget(tasks: detail.tasks),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Events Tab — chronological event timeline
// ---------------------------------------------------------------------------

class _EventsTab extends StatelessWidget {
  final ExecutionDetail detail;
  const _EventsTab({required this.detail});

  @override
  Widget build(BuildContext context) {
    if (detail.events.isEmpty) {
      return const Center(child: Text('No events persisted'));
    }

    // Consistency badge at top
    final consistency = detail.eventConsistency;
    final isConsistent = consistency?['valid'] == true;

    return Column(
      children: [
        // Consistency banner
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          color: isConsistent
              ? const Color(0xFF00FFA3).withValues(alpha: 0.08)
              : const Color(0xFFFF4D4D).withValues(alpha: 0.08),
          child: Row(
            children: [
              Icon(
                isConsistent ? Icons.verified_outlined : Icons.warning_amber_outlined,
                size: 16,
                color: isConsistent ? const Color(0xFF00FFA3) : const Color(0xFFFF4D4D),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  isConsistent
                      ? 'Event sequence is consistent ✓'
                      : 'Event inconsistency detected: ${(consistency?['issues'] as List?)?.join(', ') ?? ''}',
                  style: TextStyle(
                    fontSize: 11,
                    color: isConsistent ? const Color(0xFF00FFA3) : const Color(0xFFFF4D4D),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
        ),
        // Timeline
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
            itemCount: detail.events.length,
            itemBuilder: (context, index) {
              final event = detail.events[index];
              final isLast = index == detail.events.length - 1;
              return _EventTimelineItem(event: event, isLast: isLast);
            },
          ),
        ),
      ],
    );
  }
}

class _EventTimelineItem extends StatelessWidget {
  final ExecutionEventItem event;
  final bool isLast;

  const _EventTimelineItem({required this.event, required this.isLast});

  Color _eventColor(String type) {
    if (type.contains('completed') || type == 'agent_completed') return const Color(0xFF00FFA3);
    if (type.contains('failed')) return const Color(0xFFFF4D4D);
    if (type.contains('started')) return const Color(0xFF38BDF8);
    if (type.contains('approval')) return const Color(0xFFFF9900);
    if (type.contains('review')) return const Color(0xFF818CF8);
    return const Color(0xFF64748B);
  }

  IconData _eventIcon(String type) {
    if (type.contains('completed')) return Icons.check_circle_outline;
    if (type.contains('failed')) return Icons.error_outline;
    if (type.contains('started')) return Icons.play_arrow_outlined;
    if (type.contains('plan')) return Icons.account_tree_outlined;
    if (type.contains('approval')) return Icons.approval_outlined;
    if (type.contains('review')) return Icons.rate_review_outlined;
    if (type.contains('tool')) return Icons.build_outlined;
    return Icons.circle_outlined;
  }

  @override
  Widget build(BuildContext context) {
    final color = _eventColor(event.eventType);
    final timeStr = event.createdAt.length >= 19
        ? event.createdAt.substring(11, 19)
        : event.createdAt;

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Timeline spine
          Column(
            children: [
              Container(
                width: 28,
                height: 28,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                  border: Border.all(color: color.withValues(alpha: 0.6)),
                ),
                child: Icon(_eventIcon(event.eventType), size: 14, color: color),
              ),
              if (!isLast)
                Expanded(
                  child: Container(width: 1.5, color: const Color(0xFF1E293B)),
                ),
            ],
          ),
          const SizedBox(width: 10),
          // Event card
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFF0F1B2D),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: color.withValues(alpha: 0.2)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            event.eventType.replaceAll('_', ' ').toUpperCase(),
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: color,
                              letterSpacing: 0.6,
                            ),
                          ),
                        ),
                        Text(
                          timeStr,
                          style: const TextStyle(fontSize: 10, color: Color(0xFF64748B)),
                        ),
                      ],
                    ),
                    if (event.payloadJson != null && event.payloadJson!.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      _buildPayloadPreview(event.payloadJson!),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPayloadPreview(Map<String, dynamic> payload) {
    // Show meaningful fields only
    final interesting = {
      'goal', 'task_id', 'agent', 'status', 'confidence',
      'reason', 'error', 'tool_name', 'message', 'duration_ms'
    };
    final lines = payload.entries
        .where((e) => interesting.contains(e.key) && e.value != null)
        .map((e) => '${e.key}: ${e.value}')
        .take(4)
        .toList();

    if (lines.isEmpty) return const SizedBox.shrink();

    return Text(
      lines.join('  ·  '),
      style: const TextStyle(fontSize: 10, color: Color(0xFF94A3B8)),
      maxLines: 2,
      overflow: TextOverflow.ellipsis,
    );
  }
}

// ---------------------------------------------------------------------------
// Info Tab — metadata + actions
// ---------------------------------------------------------------------------

class _InfoTab extends StatelessWidget {
  final ExecutionDetail detail;
  final String token;

  const _InfoTab({required this.detail, required this.token});

  @override
  Widget build(BuildContext context) {
    final exec = Provider.of<ExecutionProvider>(context, listen: false);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const _SectionHeader(title: 'EXECUTION INFO'),
          const SizedBox(height: 10),
          _InfoRow(label: 'ID', value: detail.id),
          _InfoRow(label: 'Status', value: detail.status),
          _InfoRow(label: 'Goal', value: detail.goal),
          _InfoRow(label: 'Created', value: detail.createdAt),
          if (detail.startedAt != null) _InfoRow(label: 'Started', value: detail.startedAt!),
          if (detail.completedAt != null) _InfoRow(label: 'Completed', value: detail.completedAt!),
          if (detail.idempotencyKey != null) _InfoRow(label: 'Idem. Key', value: detail.idempotencyKey!),
          const SizedBox(height: 16),
          const _SectionHeader(title: 'ACTIONS'),
          const SizedBox(height: 10),
          if (detail.status == 'RUNNING' || detail.status == 'PENDING') ...[
            _ActionButton(
              icon: Icons.stop_circle_outlined,
              label: 'Cancel Execution',
              color: const Color(0xFFFF4D4D),
              onTap: () {
                exec.cancelExecution(token, detail.id);
                Navigator.of(context).pop();
              },
            ),
            const SizedBox(height: 8),
          ],
          if (detail.status == 'RUNNING') ...[
            _ActionButton(
              icon: Icons.refresh,
              label: 'Resume Execution',
              color: const Color(0xFF38BDF8),
              onTap: () {
                exec.resumeExecution(token, detail.id);
                Navigator.of(context).pop();
              },
            ),
            const SizedBox(height: 8),
          ],
          _InfoRow(label: 'Tasks', value: '${detail.tasks.length}'),
          _InfoRow(label: 'Events', value: '${detail.events.length}'),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Shared widgets
// ---------------------------------------------------------------------------

class _SectionHeader extends StatelessWidget {
  final String title;
  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.2,
            color: UltronTheme.primaryNeon,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(child: Divider(color: UltronTheme.primaryNeon.withValues(alpha: 0.2))),
      ],
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 90,
            child: Text(label, style: const TextStyle(color: Color(0xFF64748B), fontSize: 12)),
          ),
          Expanded(
            child: Text(value, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500)),
          ),
        ],
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionButton({required this.icon, required this.label, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
        icon: Icon(icon, size: 16, color: color),
        label: Text(label, style: TextStyle(color: color, fontSize: 12)),
        style: OutlinedButton.styleFrom(
          side: BorderSide(color: color.withValues(alpha: 0.5)),
          padding: const EdgeInsets.symmetric(vertical: 12),
        ),
        onPressed: onTap,
      ),
    );
  }
}
