import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/theme/ultron_theme.dart';
import 'providers/auth_provider.dart';
import 'providers/chat_provider.dart';
import 'providers/memory_provider.dart';
import 'providers/task_provider.dart';
import 'providers/execution_provider.dart';
import 'providers/workflow_provider.dart';
import 'providers/knowledge_provider.dart';
import 'providers/autonomy_provider.dart';
import 'providers/ultron_provider.dart';
import 'providers/integration_provider.dart';
import 'screens/splash/splash_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const UltronApp());
}

class UltronApp extends StatelessWidget {
  const UltronApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ChatProvider()),
        ChangeNotifierProvider(create: (_) => MemoryProvider()),
        ChangeNotifierProvider(create: (_) => TaskProvider()),
        ChangeNotifierProvider(create: (_) => ExecutionProvider()),
        ChangeNotifierProvider(create: (_) => WorkflowProvider()),
        ChangeNotifierProvider(create: (_) => KnowledgeProvider()),
        ChangeNotifierProvider(create: (_) => AutonomyProvider()),
        ChangeNotifierProvider(create: (_) => UltronProvider()),
        ChangeNotifierProvider(create: (_) => IntegrationProvider()),
      ],
      child: MaterialApp(
        title: 'ULTRON OS',
        debugShowCheckedModeBanner: false,
        theme: UltronTheme.darkTheme,
        home: const SplashScreen(),
      ),
    );
  }
}




