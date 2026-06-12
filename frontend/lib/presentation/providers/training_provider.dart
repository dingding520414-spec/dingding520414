import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';

final weeklyProgressProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final apiClient = ref.read(apiClientProvider);
  return await apiClient.getWeeklyProgress();
});

class TrainingState {
  final String? sessionId;
  final DateTime? startTime;
  final int elapsedSec;
  final bool isActive;

  TrainingState({
    this.sessionId,
    this.startTime,
    this.elapsedSec = 0,
    this.isActive = false,
  });

  TrainingState copyWith({
    String? sessionId,
    DateTime? startTime,
    int? elapsedSec,
    bool? isActive,
  }) {
    return TrainingState(
      sessionId: sessionId ?? this.sessionId,
      startTime: startTime ?? this.startTime,
      elapsedSec: elapsedSec ?? this.elapsedSec,
      isActive: isActive ?? this.isActive,
    );
  }
}

final trainingStateProvider =
    StateNotifierProvider<TrainingNotifier, TrainingState>(
        (ref) => TrainingNotifier(ref));

class TrainingNotifier extends StateNotifier<TrainingState> {
  final Ref ref;

  TrainingNotifier(this.ref) : super(TrainingState());

  Future<void> startTraining(String courseId) async {
    final apiClient = ref.read(apiClientProvider);

    try {
      final response = await apiClient.startTraining(courseId);
      state = TrainingState(
        sessionId: response['session_id'],
        startTime: DateTime.parse(response['start_time']),
        isActive: true,
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<Map<String, dynamic>> completeTraining({int? aiScore}) async {
    final apiClient = ref.read(apiClientProvider);

    if (state.sessionId == null) {
      throw Exception('No active training session');
    }

    try {
      final response = await apiClient.completeTraining(
        state.sessionId!,
        durationSec: state.elapsedSec,
        aiScore: aiScore,
      );

      state = TrainingState(); // Reset state
      return response;
    } catch (e) {
      rethrow;
    }
  }

  void updateElapsed(int seconds) {
    state = state.copyWith(elapsedSec: seconds);
  }

  void endTraining() {
    state = TrainingState();
  }
}