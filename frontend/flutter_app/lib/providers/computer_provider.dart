import 'package:flutter/material.dart';
import '../models/perception_models.dart';

class ComputerProvider with ChangeNotifier {
  String? _activeSessionId;
  int _viewportWidth = 1280;
  int _viewportHeight = 800;
  final List<ComputerActionItem> _actionHistory = [];
  ComputerActionItem? _pendingApprovalAction;

  String? get activeSessionId => _activeSessionId;
  int get viewportWidth => _viewportWidth;
  int get viewportHeight => _viewportHeight;
  List<ComputerActionItem> get actionHistory => _actionHistory;
  ComputerActionItem? get pendingApprovalAction => _pendingApprovalAction;

  void setActiveSession(String sessionId, int width, int height) {
    _activeSessionId = sessionId;
    _viewportWidth = width;
    _viewportHeight = height;
    notifyListeners();
  }

  void addAction(ComputerActionItem action) {
    _actionHistory.add(action);
    if (action.approvalState == 'REQUIRES_APPROVAL') {
      _pendingApprovalAction = action;
    }
    notifyListeners();
  }

  void clearPendingApproval() {
    _pendingApprovalAction = null;
    notifyListeners();
  }
}
