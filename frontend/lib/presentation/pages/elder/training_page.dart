import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:video_player/video_player.dart';
import 'package:youtube_player_iframe/youtube_player_iframe.dart';
import '../../../core/theme/app_theme.dart';
import '../../../data/models/course.dart';
import '../../providers/training_provider.dart';

class TrainingPage extends ConsumerStatefulWidget {
  final Course course;

  const TrainingPage({super.key, required this.course});

  @override
  ConsumerState<TrainingPage> createState() => _TrainingPageState();
}

class _TrainingPageState extends ConsumerState<TrainingPage> {
  VideoPlayerController? _videoController;
  YoutubePlayerController? _youtubeController;
  bool _isVideoInitialized = false;
  bool _isYoutube = false;
  int _currentExerciseIndex = 0;
  int _elapsedSeconds = 0;
  Timer? _timer;
  bool _isTrainingStarted = false;

  @override
  void initState() {
    super.initState();
    _initializeVideo();
  }

  Future<void> _initializeVideo() async {
    if (widget.course.videoUrl == null) return;
    final url = widget.course.videoUrl!;
    if (url.contains('youtube.com') || url.contains('youtu.be')) {
      // YouTube video
      _isYoutube = true;
      final videoId = _extractYoutubeId(url);
      if (videoId != null) {
        _youtubeController = YoutubePlayerController.fromVideoId(
          videoId: videoId,
          autoPlay: false,
        );
        setState(() => _isVideoInitialized = true);
      }
    } else {
      // Direct video URL
      _isYoutube = false;
      _videoController = VideoPlayerController.networkUrl(Uri.parse(url));
      await _videoController!.initialize();
      setState(() => _isVideoInitialized = true);
    }
  }

  String? _extractYoutubeId(String url) {
    final patterns = [
      RegExp(r'youtube\.com/embed/([^?&]+)'),
      RegExp(r'youtube\.com/watch\?v=([^&]+)'),
      RegExp(r'youtu\.be/([^?]+)'),
    ];
    for (final p in patterns) {
      final m = p.firstMatch(url);
      if (m != null) return m.group(1);
    }
    return null;
  }

  void _startTraining() async {
    try {
      await ref
          .read(trainingStateProvider.notifier)
          .startTraining(widget.course.id);
      setState(() => _isTrainingStarted = true);
      _startTimer();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('开始训练失败: $e')),
        );
      }
    }
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() => _elapsedSeconds++);
      ref.read(trainingStateProvider.notifier).updateElapsed(_elapsedSeconds);
    });
  }

  void _stopTimer() {
    _timer?.cancel();
  }

  Future<void> _completeTraining() async {
    _stopTimer();
    try {
      await ref.read(trainingStateProvider.notifier).completeTraining();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('训练完成！继续保持！'),
            backgroundColor: AppColors.success,
          ),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('完成训练失败: $e')),
        );
      }
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    _videoController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final exercises = widget.course.exercises;
    final currentExercise = exercises.isNotEmpty ? exercises[_currentExerciseIndex] : null;

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.course.title),
        actions: [
          if (_isTrainingStarted)
            Center(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.timer, size: 18, color: AppColors.primary),
                    const SizedBox(width: 4),
                    Text(
                      _formatTime(_elapsedSeconds),
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        color: AppColors.primary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          const SizedBox(width: 16),
        ],
      ),
      body: Column(
        children: [
          // Video Player Area
          Container(
            height: MediaQuery.of(context).size.height * 0.4,
            width: double.infinity,
            color: Colors.black,
            child: _isVideoInitialized && !_isYoutube && _videoController != null
                ? AspectRatio(
                    aspectRatio: _videoController!.value.aspectRatio,
                    child: VideoPlayer(_videoController!),
                  )
                : _isVideoInitialized && _isYoutube && _youtubeController != null
                ? YoutubePlayer(controller: _youtubeController!)
                : const Center(
                    child: Icon(
                      Icons.play_circle_outline,
                      size: 80,
                      color: Colors.white54,
                    ),
                  ),
          ),

          // Exercise Info
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Progress Indicator
                  Row(
                    children: List.generate(exercises.length, (index) {
                      return Expanded(
                        child: Container(
                          height: 4,
                          margin: const EdgeInsets.symmetric(horizontal: 2),
                          decoration: BoxDecoration(
                            color: index <= _currentExerciseIndex
                                ? AppColors.primary
                                : AppColors.textTertiary,
                            borderRadius: BorderRadius.circular(2),
                          ),
                        ),
                      );
                    }),
                  ),
                  const SizedBox(height: 24),

                  // Current Exercise
                  if (currentExercise != null) ...[
                    Text(
                      currentExercise.name,
                      style: Theme.of(context).textTheme.headlineMedium,
                    ),
                    const SizedBox(height: 8),
                    if (currentExercise.description != null)
                      Text(
                        currentExercise.description!,
                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                              color: AppColors.textSecondary,
                            ),
                      ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        if (currentExercise.reps != null)
                          _buildInfoChip(
                            Icons.repeat,
                            '${currentExercise.reps} 次',
                          ),
                        const SizedBox(width: 12),
                        if (currentExercise.durationSec != null)
                          _buildInfoChip(
                            Icons.timer,
                            '${currentExercise.durationSec} 秒',
                          ),
                      ],
                    ),
                  ],

                  const Spacer(),

                  // Navigation Buttons
                  Row(
                    children: [
                      if (_currentExerciseIndex > 0)
                        Expanded(
                          child: OutlinedButton(
                            onPressed: () {
                              setState(() => _currentExerciseIndex--);
                            },
                            child: const Text('上一个'),
                          ),
                        ),
                      const SizedBox(width: 16),
                      if (_currentExerciseIndex < exercises.length - 1)
                        Expanded(
                          child: ElevatedButton(
                            onPressed: () {
                              setState(() => _currentExerciseIndex++);
                            },
                            child: const Text('下一个'),
                          ),
                        )
                      else
                        Expanded(
                          child: ElevatedButton(
                            onPressed: _isTrainingStarted
                                ? _completeTraining
                                : _startTraining,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.success,
                            ),
                            child: Text(
                              _isTrainingStarted ? '完成训练' : '开始训练',
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoChip(IconData icon, String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.primary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        children: [
          Icon(icon, size: 18, color: AppColors.primary),
          const SizedBox(width: 4),
          Text(
            text,
            style: const TextStyle(
              color: AppColors.primary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  String _formatTime(int seconds) {
    final minutes = seconds ~/ 60;
    final secs = seconds % 60;
    return '${minutes.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}';
  }
}