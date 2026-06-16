import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/subscription.dart';
import '../../core/network/api_client.dart';

/// API service for subscription endpoints
class SubscriptionApiService {
  final ApiClient _apiClient;

  SubscriptionApiService({required ApiClient apiClient}) : _apiClient = apiClient;

  Future<SubscriptionStatus> getStatus() async {
    try {
      final response = await _apiClient.getSubscriptionStatus();
      return SubscriptionStatus.fromJson(response as Map<String, dynamic>);
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> createSubscription({
    required String planType,
    required String interval,
  }) async {
    try {
      final response = await _apiClient.createSubscription(planType, interval: interval);
      return response;
    } catch (e) {
      rethrow;
    }
  }

  Future<void> cancelSubscription() async {
    try {
      await _apiClient.cancelSubscription();
    } catch (e) {
      rethrow;
    }
  }
}

/// Subscription state
class SubscriptionState {
  final SubscriptionStatus? status;
  final bool isLoading;
  final String? error;
  final int selectedTab; // 0 = monthly, 1 = yearly
  final bool mockModeSuccess;

  SubscriptionState({
    this.status,
    this.isLoading = false,
    this.error,
    this.selectedTab = 0,
    this.mockModeSuccess = false,
  });

  SubscriptionState copyWith({
    SubscriptionStatus? status,
    bool? isLoading,
    String? error,
    int? selectedTab,
    bool? mockModeSuccess,
  }) {
    return SubscriptionState(
      status: status ?? this.status,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      selectedTab: selectedTab ?? this.selectedTab,
      mockModeSuccess: mockModeSuccess ?? this.mockModeSuccess,
    );
  }
}

/// Subscription notifier
class SubscriptionNotifier extends StateNotifier<SubscriptionState> {
  final SubscriptionApiService _apiService;

  SubscriptionNotifier(this._apiService) : super(SubscriptionState());

  Future<void> loadStatus() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final status = await _apiService.getStatus();
      state = state.copyWith(status: status, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void setSelectedTab(int tab) {
    state = state.copyWith(selectedTab: tab);
  }

  Future<void> subscribe(String planType, String interval) async {
    state = state.copyWith(isLoading: true, error: null, mockModeSuccess: false);
    try {
      final result = await _apiService.createSubscription(
        planType: planType,
        interval: interval,
      );

      // Check if mock mode (no checkout URL)
      if (result['mock_mode'] == true || result['checkout_url'] == null) {
        // Reload status to get updated subscription info
        await loadStatus();
        state = state.copyWith(mockModeSuccess: true);
      } else {
        // Real Stripe mode - would navigate to checkout_url
        await loadStatus();
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> cancelSubscription() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await _apiService.cancelSubscription();
      await loadStatus();
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void clearMockSuccess() {
    state = state.copyWith(mockModeSuccess: false);
  }
}

/// Provider for subscription state
final subscriptionProvider =
    StateNotifierProvider<SubscriptionNotifier, SubscriptionState>((ref) {
  // Get API client from provider
  final apiClient = ref.watch(apiClientProvider);
  final apiService = SubscriptionApiService(apiClient: apiClient);
  return SubscriptionNotifier(apiService);
});
