import 'package:flutter/material.dart';
import '../models/code_models.dart';

class CodeProvider extends ChangeNotifier {
  List<CodeWorkspace> _workspaces = [];
  CodeWorkspace? _activeWorkspace;
  CodeFile? _activeFile;
  CodeExecution? _currentExecution;
  List<CodeArtifact> _artifacts = [];
  List<CodeTestItem> _testResults = [];
  List<Map<String, dynamic>> _timelineEvents = [];
  bool _isExecuting = false;
  String _diffText = '';

  List<CodeWorkspace> get workspaces => _workspaces;
  CodeWorkspace? get activeWorkspace => _activeWorkspace;
  CodeFile? get activeFile => _activeFile;
  CodeExecution? get currentExecution => _currentExecution;
  List<CodeArtifact> get artifacts => _artifacts;
  List<CodeTestItem> get testResults => _testResults;
  List<Map<String, dynamic>> get timelineEvents => _timelineEvents;
  bool get isExecuting => _isExecuting;
  String get diffText => _diffText;

  void setWorkspaces(List<CodeWorkspace> workspaces) {
    _workspaces = workspaces;
    if (_workspaces.isNotEmpty && _activeWorkspace == null) {
      _activeWorkspace = _workspaces.first;
    }
    notifyListeners();
  }

  void setActiveWorkspace(CodeWorkspace workspace) {
    _activeWorkspace = workspace;
    if (workspace.files.isNotEmpty) {
      _activeFile = workspace.files.first;
    } else {
      _activeFile = null;
    }
    notifyListeners();
  }

  void setActiveFile(CodeFile file) {
    _activeFile = file;
    notifyListeners();
  }

  void setExecution(CodeExecution execution) {
    _currentExecution = execution;
    notifyListeners();
  }

  void setExecuting(bool executing) {
    _isExecuting = executing;
    notifyListeners();
  }

  void addTimelineEvent(Map<String, dynamic> event) {
    _timelineEvents.add(event);
    notifyListeners();
  }

  void setArtifacts(List<CodeArtifact> artifacts) {
    _artifacts = artifacts;
    notifyListeners();
  }

  void setTestResults(List<CodeTestItem> tests) {
    _testResults = tests;
    notifyListeners();
  }

  void setDiffText(String diff) {
    _diffText = diff;
    notifyListeners();
  }

  void clearTimeline() {
    _timelineEvents.clear();
    notifyListeners();
  }
}
