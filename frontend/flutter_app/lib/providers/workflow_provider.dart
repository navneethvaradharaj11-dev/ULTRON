import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/workflow_models.dart';
import '../services/websocket_service.dart';
import '../services/api_service.dart';

class WorkflowProvider with ChangeNotifier {
  List<WorkflowModel> _workflows = [];
  WorkflowModel? _activeWorkflow;
  List<WorkflowStepModel> _activeSteps = [];
  List<WorkflowEventModel> _activeEvents = [];
  WorkflowResultModel? _activeResult;
  List<WorkflowArtifactModel> _activeArtifacts = [];
  List<WorkflowApprovalModel> _activeApprovals = [];
  List<String> _notifications = [];
  bool _isLoading = false;
  String? _error;

  final WebSocketService _wsService = WebSocketService();

  List<WorkflowModel> get workflows => _workflows;
  WorkflowModel? get activeWorkflow => _activeWorkflow;
  List<WorkflowStepModel> get activeSteps => _activeSteps;
  List<WorkflowEventModel> get activeEvents => _activeEvents;
  WorkflowResultModel? get activeResult => _activeResult;
  List<WorkflowArtifactModel> get activeArtifacts => _activeArtifacts;
  List<WorkflowApprovalModel> get activeApprovals => _activeApprovals;
  List<String> get notifications => _notifications;
  bool get isLoading => _isLoading;
  String? get error => _error;

  static String get baseUrl => '${ApiService.baseUrl}/workflows';

  void addNotification(String msg) {
    _notifications.insert(0, msg);
    notifyListeners();
  }

  void clearNotifications() {
    _notifications.clear();
    notifyListeners();
  }

  Future<void> fetchWorkflows(String token) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final res = await http.get(
        Uri.parse(baseUrl),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        final List list = jsonDecode(res.body);
        _workflows = list.map((item) => WorkflowModel.fromJson(item)).toList();
      } else {
        _error = 'Failed to fetch workflows';
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<WorkflowModel?> createWorkflow(String token, String goal) async {
    try {
      final res = await http.post(
        Uri.parse(baseUrl),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json'
        },
        body: jsonEncode({'goal': goal}),
      );
      if (res.statusCode == 201) {
        final data = jsonDecode(res.body);
        final wf = WorkflowModel.fromJson(data);
        _workflows.insert(0, wf);
        notifyListeners();
        return wf;
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
    return null;
  }

  Future<void> startWorkflow(String token, String workflowId) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/$workflowId/start'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        addNotification('Workflow $workflowId started');
        fetchWorkflowDetail(token, workflowId);
        connectRealtimeStream(workflowId, token);
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> pauseWorkflow(String token, String workflowId) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/$workflowId/pause'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        addNotification('Workflow $workflowId paused server-side');
        fetchWorkflowDetail(token, workflowId);
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> resumeWorkflow(String token, String workflowId) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/$workflowId/resume'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        addNotification('Workflow $workflowId resumed server-side');
        fetchWorkflowDetail(token, workflowId);
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> cancelWorkflow(String token, String workflowId) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/$workflowId/cancel'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        addNotification('Workflow $workflowId cancelled server-side');
        fetchWorkflowDetail(token, workflowId);
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> approveDecision(String token, String workflowId, String approvalId, bool approved) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/$workflowId/approve'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json'
        },
        body: jsonEncode({'approval_id': approvalId, 'approved': approved}),
      );
      if (res.statusCode == 200) {
        addNotification(approved ? 'Approval granted' : 'Approval denied');
        fetchApprovals(token, workflowId);
        fetchWorkflowDetail(token, workflowId);
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> fetchWorkflowDetail(String token, String workflowId) async {
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/$workflowId'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        _activeWorkflow = WorkflowModel.fromJson(jsonDecode(res.body));
        fetchSteps(token, workflowId);
        fetchEvents(token, workflowId);
        fetchResult(token, workflowId);
        fetchArtifacts(token, workflowId);
        fetchApprovals(token, workflowId);
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      notifyListeners();
    }
  }

  Future<void> fetchSteps(String token, String workflowId) async {
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/$workflowId/steps'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        final List list = jsonDecode(res.body);
        _activeSteps = list.map((s) => WorkflowStepModel.fromJson(s)).toList();
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> fetchEvents(String token, String workflowId) async {
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/$workflowId/events'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        final List list = jsonDecode(res.body);
        _activeEvents = list.map((e) => WorkflowEventModel.fromJson(e)).toList();
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> fetchResult(String token, String workflowId) async {
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/$workflowId/result'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        _activeResult = WorkflowResultModel.fromJson(jsonDecode(res.body));
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> fetchArtifacts(String token, String workflowId) async {
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/$workflowId/artifacts'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        final List list = jsonDecode(res.body);
        _activeArtifacts = list.map((a) => WorkflowArtifactModel.fromJson(a)).toList();
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> fetchApprovals(String token, String workflowId) async {
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/$workflowId/approvals'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (res.statusCode == 200) {
        final List list = jsonDecode(res.body);
        _activeApprovals = list.map((ap) => WorkflowApprovalModel.fromJson(ap)).toList();
        notifyListeners();
      }
    } catch (_) {}
  }

  void connectRealtimeStream(String workflowId, String token) {
    _wsService.onEvent = (event) {
      if (event['event_type'] != null) {
        addNotification('Realtime Event: ${event['event_type']}');
        fetchWorkflowDetail(token, workflowId);
      }
    };
    _wsService.connectWorkflowStream(workflowId, token);
  }

  @override
  void dispose() {
    _wsService.disconnect();
    super.dispose();
  }
}
