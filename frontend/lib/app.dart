import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/theme/app_theme.dart';
import 'core/network/api_client.dart';
import 'presentation/providers/auth_provider.dart';
import 'presentation/pages/elder/home_page.dart';
import 'presentation/pages/adult/family_dashboard_page.dart';
import 'presentation/pages/auth/login_page.dart';

class SeniorStrengthApp extends ConsumerStatefulWidget {
  const SeniorStrengthApp({super.key});

  @override
  ConsumerState<SeniorStrengthApp> createState() => _SeniorStrengthAppState();
}

class _SeniorStrengthAppState extends ConsumerState<SeniorStrengthApp> {
  @override
  void initState() {
    super.initState();
    // Initialize API client
    ref.read(apiClientProvider);
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authStateProvider);

    return MaterialApp(
      title: 'SeniorStrength',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: authState.when(
        data: (user) {
          if (user == null) {
            return const LoginPage();
          }
          // Check user role and navigate accordingly
          // For now, default to elder home
          return const ElderHomePage();
        },
        loading: () => const Scaffold(
          body: Center(
            child: CircularProgressIndicator(),
          ),
        ),
        error: (err, stack) => Scaffold(
          body: Center(
            child: Text('Error: $err'),
          ),
        ),
      ),
    );
  }
}