import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/ultron_theme.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/ultron_status.dart';
import '../chat/chat_screen.dart';
import '../execution/execution_screen.dart';
import '../memory/memory_screen.dart';
import '../tasks/tasks_screen.dart';
import '../settings/settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    ChatScreen(),
    ExecutionScreen(),
    MemoryScreen(),
    TasksScreen(),
    SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('ULTRON OS'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: UltronTheme.error),
            onPressed: () => auth.logout(),
          ),
        ],
      ),
      body: Column(
        children: [
          const Padding(
            padding: EdgeInsets.fromLTRB(12, 8, 12, 0),
            child: UltronStatusCard(),
          ),
          Expanded(child: _screens[_currentIndex]),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        selectedItemColor: UltronTheme.primaryNeon,
        unselectedItemColor: UltronTheme.textMuted,
        backgroundColor: const Color(0xFF0F172A),
        type: BottomNavigationBarType.fixed,
        onTap: (idx) => setState(() => _currentIndex = idx),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.chat_bubble_outline), label: 'Chat'),
          BottomNavigationBarItem(icon: Icon(Icons.account_tree_outlined), label: 'Executions'),
          BottomNavigationBarItem(icon: Icon(Icons.psychology_outlined), label: 'Memory'),
          BottomNavigationBarItem(icon: Icon(Icons.task_alt_outlined), label: 'Tasks'),
          BottomNavigationBarItem(icon: Icon(Icons.settings_outlined), label: 'Settings'),
        ],
      ),
    );
  }
}
