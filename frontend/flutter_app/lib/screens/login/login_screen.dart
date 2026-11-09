import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/ultron_theme.dart';
import '../../providers/auth_provider.dart';
import '../home/home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _userController = TextEditingController(text: 'ultron_user');
  final _emailController = TextEditingController(text: 'user@ultron.ai');
  final _passController = TextEditingController(text: 'SecretPassword123');
  bool _isRegister = false;
  String _errorMsg = '';

  Future<void> _submit() async {
    setState(() { _errorMsg = ''; });
    final auth = Provider.of<AuthProvider>(context, listen: false);

    try {
      if (_isRegister) {
        await auth.register(_userController.text, _emailController.text, _passController.text);
        if (!mounted) return;
        setState(() { _isRegister = false; });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Registration successful! Please login.')),
        );
      } else {
        final success = await auth.login(_userController.text, _passController.text);
        if (success && mounted) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (_) => const HomeScreen()),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() { _errorMsg = e.toString().replaceAll('Exception: ', ''); });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    return Scaffold(
      body: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 400),
          padding: const EdgeInsets.all(24),
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Center(
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: UltronTheme.primaryNeon.withOpacity(0.3),
                            blurRadius: 16,
                            spreadRadius: 2,
                          ),
                        ],
                      ),
                      child: ClipOval(
                        child: Image.asset(
                          'assets/images/ultron_icon.png',
                          width: 72,
                          height: 72,
                          fit: BoxFit.contain,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    _isRegister ? 'REGISTER ULTRON' : 'LOGIN TO ULTRON',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.5,
                      color: UltronTheme.primaryNeon,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 20),
                  if (_errorMsg.isNotEmpty) ...[
                    Text(_errorMsg, style: const TextStyle(color: UltronTheme.error, fontSize: 12)),
                    const SizedBox(height: 10),
                  ],
                  TextField(
                    controller: _userController,
                    decoration: const InputDecoration(labelText: 'Username'),
                  ),
                  const SizedBox(height: 12),
                  if (_isRegister) ...[
                    TextField(
                      controller: _emailController,
                      decoration: const InputDecoration(labelText: 'Email'),
                    ),
                    const SizedBox(height: 12),
                  ],
                  TextField(
                    controller: _passController,
                    obscureText: true,
                    decoration: const InputDecoration(labelText: 'Password'),
                  ),
                  const SizedBox(height: 24),
                  auth.isLoading
                      ? const Center(child: CircularProgressIndicator())
                      : ElevatedButton(
                          onPressed: _submit,
                          child: Text(_isRegister ? 'REGISTER' : 'LOGIN'),
                        ),
                  TextButton(
                    onPressed: () => setState(() => _isRegister = !_isRegister),
                    child: Text(
                      _isRegister ? 'Already have an account? Login' : "Don't have an account? Register",
                      style: const TextStyle(color: UltronTheme.accentCyan),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
