import 'package:flutter/material.dart';
import '../models/perception_models.dart';

class PerceptionProvider with ChangeNotifier {
  List<PerceptionElement> _elements = [];
  double _confidence = 1.0;
  String _ocrText = '';
  List<String> _warnings = [];
  bool _isLoading = false;

  List<PerceptionElement> get elements => _elements;
  double get confidence => _confidence;
  String get ocrText => _ocrText;
  List<String> get warnings => _warnings;
  bool get isLoading => _isLoading;

  void setPerceptionData(Map<String, dynamic> data) {
    final rawElements = (data['elements'] as List?) ?? [];
    _elements = rawElements.map((e) => PerceptionElement.fromJson(Map<String, dynamic>.from(e))).toList();
    _confidence = (data['confidence'] as num?)?.toDouble() ?? 1.0;
    _ocrText = data['ocr_text'] ?? '';
    _warnings = List<String>.from(data['warnings'] ?? []);
    notifyListeners();
  }

  void setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
}
