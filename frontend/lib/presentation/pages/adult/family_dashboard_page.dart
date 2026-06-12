import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_theme.dart';

class FamilyDashboardPage extends ConsumerWidget {
  const FamilyDashboardPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('家庭健康看板'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {},
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Family Members
            Text(
              '家庭成员',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 16),
            _buildElderCard(
              context,
              name: '张爷爷',
              streakDays: 7,
              weeklyCheckins: 5,
              lastTraining: '2小时前',
              avatarUrl: null,
            ),
            const SizedBox(height: 24),

            // Quick Actions
            Text(
              '快捷操作',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildQuickActionCard(
                    context,
                    icon: Icons.person_add_outlined,
                    label: '添加成员',
                    onTap: () {},
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildQuickActionCard(
                    context,
                    icon: Icons.family_restroom,
                    label: '家庭设置',
                    onTap: () {},
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Recent Activity
            Text(
              '最近活动',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 16),
            _buildActivityItem(
              context,
              icon: Icons.check_circle,
              color: AppColors.success,
              title: '张爷爷完成训练',
              subtitle: '椅子深蹲入门 · 10分钟',
              time: '2小时前',
            ),
            _buildActivityItem(
              context,
              icon: Icons.celebration,
              color: AppColors.warning,
              title: '达成7天连续训练',
              subtitle: '太棒了！继续保持',
              time: '昨天',
            ),
            _buildActivityItem(
              context,
              icon: Icons.thumb_up,
              color: AppColors.info,
              title: '收到鼓励消息',
              subtitle: '加油！坚持就是胜利',
              time: '2天前',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildElderCard(
    BuildContext context, {
    required String name,
    required int streakDays,
    required int weeklyCheckins,
    required String lastTraining,
    String? avatarUrl,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 30,
                  backgroundColor: AppColors.primary.withOpacity(0.1),
                  child: avatarUrl != null
                      ? null
                      : const Icon(
                          Icons.person,
                          size: 36,
                          color: AppColors.primary,
                        ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        name,
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          const Icon(
                            Icons.local_fire_department,
                            color: AppColors.streakFlame,
                            size: 18,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '$streakDays天连续',
                            style: const TextStyle(
                              color: AppColors.streakFlame,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.chevron_right),
                  onPressed: () {
                    // Navigate to elder detail
                  },
                ),
              ],
            ),
            const Divider(height: 32),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatColumn(
                  context,
                  value: '$weeklyCheckins',
                  label: '本周训练',
                  icon: Icons.fitness_center,
                ),
                _buildStatColumn(
                  context,
                  value: lastTraining,
                  label: '上次训练',
                  icon: Icons.schedule,
                ),
                _buildStatColumn(
                  context,
                  value: '5',
                  label: '本月完成',
                  icon: Icons.check_circle_outline,
                ),
              ],
            ),
            const SizedBox(height: 16),
            // Encouragement Button
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {
                  _showEncouragementDialog(context);
                },
                icon: const Icon(Icons.favorite_outline),
                label: const Text('发送鼓励'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatColumn(
    BuildContext context, {
    required String value,
    required String label,
    required IconData icon,
  }) {
    return Column(
      children: [
        Icon(icon, color: AppColors.textSecondary, size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }

  Widget _buildQuickActionCard(
    BuildContext context, {
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              Icon(icon, size: 32, color: AppColors.primary),
              const SizedBox(height: 8),
              Text(
                label,
                style: Theme.of(context).textTheme.labelLarge,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildActivityItem(
    BuildContext context, {
    required IconData icon,
    required Color color,
    required String title,
    required String subtitle,
    required String time,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
                Text(
                  subtitle,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
          Text(
            time,
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }

  void _showEncouragementDialog(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '发送鼓励',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 16),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _buildEmojiButton('👍', '加油！'),
                  _buildEmojiButton('❤️', '我们支持你'),
                  _buildEmojiButton('🎉', '太棒了！'),
                  _buildEmojiButton('💪', '继续坚持'),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildEmojiButton(String emoji, String label) {
    return ActionChip(
      label: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 18)),
          const SizedBox(width: 4),
          Text(label),
        ],
      ),
      onPressed: () {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('已发送: $label')),
        );
      },
    );
  }
}