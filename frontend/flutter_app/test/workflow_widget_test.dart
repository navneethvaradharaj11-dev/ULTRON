import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_app/models/workflow_models.dart';

void main() {
  test('WorkflowModel JSON parsing test', () {
    final json = {
      'id': 'wf_100',
      'goal': 'Autonomous Research Goal',
      'current_state': 'RUNNING',
      'progress': 0.75,
      'retry_count': 1,
      'replan_count': 0,
      'created_at': '2026-08-28T12:00:00Z',
      'updated_at': '2026-08-28T12:05:00Z'
    };

    final model = WorkflowModel.fromJson(json);
    expect(model.workflowId, 'wf_100');
    expect(model.goal, 'Autonomous Research Goal');
    expect(model.state, 'RUNNING');
    expect(model.progress, 0.75);
    expect(model.retryCount, 1);
  });
}
