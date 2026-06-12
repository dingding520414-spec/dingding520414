import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_theme.dart';
import '../../providers/course_provider.dart';
import '../../providers/training_provider.dart';
import '../../widgets/course_card.dart';
import '../../widgets/progress_chart.dart';
import 'training_page.dart';

class ElderHomePage extends ConsumerStatefulWidget {
  const ElderHomePage({super.key});

  @override
  ConsumerState<ElderHomePage> createState() => _ElderHomePageState();
}

class _ElderHomePageState extends ConsumerState<ElderHomePage> {
  int _selectedDifficulty = 0; // 0 = All

  @override
  Widget build(BuildContext context) {
    final coursesAsync = ref.watch(coursesProvider(
      _selectedDifficulty == 0 ? null : _selectedDifficulty,
    ));
    final weeklyProgress = ref.watch(weeklyProgressProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('力量训练'),
        actions: [
          IconButton(
            icon: const Icon(Icons.person_outlined),
            onPressed: () {
              // Navigate to profile
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(coursesProvider(null));
          ref.invalidate(weeklyProgressProvider);
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Weekly Progress Card
              weeklyProgress.when(
                data: (progress) => _buildProgressCard(progress),
                loading: () => const Center(
                  child: Padding(
                    padding: EdgeInsets.all(16),
                    child: CircularProgressIndicator(),
                  ),
                ),
                error: (_, __) => const SizedBox.shrink(),
              ),

              // Course Filter
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Row(
                  children: [
                    _buildFilterChip(0, '全部'),
                    const SizedBox(width: 8),
                    _buildFilterChip(1, '★☆☆☆☆'),
                    const SizedBox(width: 8),
                    _buildFilterChip(2, '★★☆☆☆'),
                    const SizedBox(width: 8),
                    _buildFilterChip(3, '★★★☆☆'),
                  ],
                ),
              ),
              const SizedBox(height: 8),

              // Course List
              coursesAsync.when(
                data: (courses) {
                  if (courses.isEmpty) {
                    return const Center(
                      child: Padding(
                        padding: EdgeInsets.all(32),
                        child: Text('暂无课程'),
                      ),
                    );
                  }
                  return ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount: courses.length,
                    itemBuilder: (context, index) {
                      final course = courses[index];
                      return CourseCard(
                        course: course,
                        onTap: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => TrainingPage(course: course),
                            ),
                          );
                        },
                      );
                    },
                  );
                },
                loading: () => const Center(
                  child: Padding(
                    padding: EdgeInsets.all(32),
                    child: CircularProgressIndicator(),
                  ),
                ),
                error: (error, _) => Center(
                  child: Padding(
                    padding: const EdgeInsets.all(32),
                    child: Text('加载失败: $error'),
                  ),
                ),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProgressCard(Map<String, dynamic> progress) {
    final streakDays = progress['streak_days'] ?? 0;
    final totalDurationMin = progress['total_duration_min'] ?? 0;
    final checkins = progress['checkins'] as List? ?? [];

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppColors.primary, AppColors.primaryDark],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                '本周训练',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.local_fire_department,
                        color: AppColors.streakFlame, size: 20),
                    const SizedBox(width: 4),
                    Text(
                      '$streakDays 天连续',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              _buildStatItem(
                icon: Icons.check_circle_outline,
                value: '${checkins.length}',
                label: '训练次数',
              ),
              const SizedBox(width: 24),
              _buildStatItem(
                icon: Icons.timer_outlined,
                value: '${totalDurationMin}',
                label: '总时长(分钟)',
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Progress Chart
          SizedBox(
            height: 60,
            child: ProgressChart(checkins: checkins),
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String value,
    required String label,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: Colors.white70, size: 20),
            const SizedBox(width: 8),
            Text(
              value,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 14,
          ),
        ),
      ],
    );
  }

  Widget _buildFilterChip(int difficulty, String label) {
    final isSelected = _selectedDifficulty == difficulty;
    return GestureDetector(
      onTap: () {
        setState(() => _selectedDifficulty = difficulty);
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primary : AppColors.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? AppColors.primary : AppColors.textTertiary,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isSelected ? Colors.white : AppColors.textSecondary,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
          ),
        ),
      ),
    );
  }
}