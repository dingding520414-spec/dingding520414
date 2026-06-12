import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../core/network/api_client.dart';
import '../../data/models/user.dart';

final authStateProvider =
    AsyncNotifierProvider<AuthNotifier, User?>(() => AuthNotifier());

class AuthNotifier extends AsyncNotifier<User?> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  @override
  Future<User?> build() async {
    final apiClient = ref.read(apiClientProvider);
    final token = await apiClient.getAccessToken();
    if (token == null) return null;

    try {
      final userData = await apiClient.getCurrentUser();
      return User.fromJson(userData);
    } catch (e) {
      // Token invalid, clear it
      await apiClient.clearTokens();
      return null;
    }
  }

  Future<void> login({
    String? email,
    String? phone,
    required String password,
  }) async {
    final apiClient = ref.read(apiClientProvider);

    state = const AsyncValue.loading();
    try {
      final response = await apiClient.login(
        email: email,
        phone: phone,
        password: password,
      );

      await apiClient.saveTokens(
        response['access_token'],
        response['refresh_token'],
      );

      state = AsyncValue.data(User.fromJson(response['user']));
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
      rethrow;
    }
  }

  Future<void> register({
    String? email,
    String? phone,
    required String password,
    required String name,
    int? age,
    String role = 'elder',
  }) async {
    final apiClient = ref.read(apiClientProvider);

    state = const AsyncValue.loading();
    try {
      final response = await apiClient.register(
        email: email,
        phone: phone,
        password: password,
        name: name,
        age: age,
        role: role,
      );

      await apiClient.saveTokens(
        response['access_token'],
        response['refresh_token'],
      );

      state = AsyncValue.data(User.fromJson(response['user']));
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
      rethrow;
    }
  }

  Future<void> logout() async {
    final apiClient = ref.read(apiClientProvider);
    await apiClient.clearTokens();
    state = const AsyncValue.data(null);
  }
}