import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/subscription.dart';

/// API service for subscription endpoints
class SubscriptionApiService {
  final String baseUrl;

  SubscriptionApiService({required this.baseUrl});

  Future<SubscriptionStatus> getStatus(String token) async {
    // TODO: Call API when backend is ready
    // For now, return mock data
    await Future.delayed(const Duration(milliseconds: 300));
    return SubscriptionStatus(
      planType: 'free',
      status: 'active',
      isActive: false,
      trialDaysRemaining: 7,
    );
  }

  Future<bool> startTrial(String token, String planType) async {
    // TODO: Call API when backend is ready
    await Future.delayed(const Duration(milliseconds: 500));
    return true;
  }

  Future<Map<String, dynamic>> createCheckout(String token, String planType, String interval) async {
    // TODO: Call API when backend Stripe is configured
    await Future.delayed(const Duration(milliseconds: 500));
    return {
      'checkout_url': 'https://checkout.stripe.com/mock',
      'session_id': 'mock_session_id',
    };
  }
}

/// Subscription state
class SubscriptionState {
  final SubscriptionStatus? status;
  final bool isLoading;
  final String? error;
  final int selectedTab; // 0 = monthly, 1 = yearly

  SubscriptionState({
    this.status,
    this.isLoading = false,
    this.error,
    this.selectedTab = 0,
  });

  SubscriptionState copyWith({
    SubscriptionStatus? status,
    bool? isLoading,
    String? error,
    int? selectedTab,
  }) {
    return SubscriptionState(
      status: status ?? this.status,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      selectedTab: selectedTab ?? this.selectedTab,
    );
  }
}

/// Subscription notifier
class SubscriptionNotifier extends StateNotifier<SubscriptionState> {
  final SubscriptionApiService _apiService;
  final String _token;

  SubscriptionNotifier(this._apiService, this._token) : super(SubscriptionState());

  Future<void> loadStatus() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final status = await _apiService.getStatus(_token);
      state = state.copyWith(status: status, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void setSelectedTab(int tab) {
    state = state.copyWith(selectedTab: tab);
  }

  Future<void> startTrial(String planType) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await _apiService.startTrial(_token, planType);
      await loadStatus();
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> subscribe(String planType, String interval) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final result = await _apiService.createCheckout(_token, planType, interval);
      // In real app, navigate to Stripe checkout URL
      // For now, just reload status
      await loadStatus();
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

/// Provider for subscription state
final subscriptionProvider =
    StateNotifierProvider<SubscriptionNotifier, SubscriptionState>((ref) {
  // TODO: Get actual base URL from config
  const apiService = SubscriptionApiService(baseUrl: 'http://localhost:8080/api/v1');
  // TODO: Get actual token from auth provider
  const token = '';
  return SubscriptionNotifier(apiService, token);
});
