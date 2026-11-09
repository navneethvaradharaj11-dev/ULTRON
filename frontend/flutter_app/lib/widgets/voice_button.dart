import 'package:flutter/material.dart';
import '../core/theme/ultron_theme.dart';

class VoiceButton extends StatefulWidget {
  final Function(String) onVoiceInput;

  const VoiceButton({super.key, required this.onVoiceInput});

  @override
  State<VoiceButton> createState() => _VoiceButtonState();
}

class _VoiceButtonState extends State<VoiceButton> {
  bool _isListening = false;

  void _toggleListening() {
    setState(() {
      _isListening = !_isListening;
    });

    if (!_isListening) {
      widget.onVoiceInput("Calculate 15 * 8");
    }
  }

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: Icon(
        _isListening ? Icons.mic : Icons.mic_none,
        color: _isListening ? UltronTheme.error : UltronTheme.primaryNeon,
      ),
      onPressed: _toggleListening,
      tooltip: _isListening ? 'Listening...' : 'Voice Input',
    );
  }
}
