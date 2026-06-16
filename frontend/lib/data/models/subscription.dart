/// Subscription plan information
class SubscriptionPlan {
  final String id;
  final String name;
  final String description;
  final double monthlyPrice;
  final double yearlyPrice;
  final int maxMembers;
  final List<String> features;
  final bool isRecommended;

  const SubscriptionPlan({
    required this.id,
    required this.name,
    required this.description,
    required this.monthlyPrice,
    required this.yearlyPrice,
    required this.maxMembers,
    required this.features,
    this.isRecommended = false,
  });
}

/// Current subscription status
class SubscriptionStatus {
  final String planType; // 'free', 'personal', 'family'
  final String status; // 'active', 'cancelled', 'expired'
  final DateTime? currentPeriodStart;
  final DateTime? currentPeriodEnd;
  final bool isActive;
  final int trialDaysRemaining;

  SubscriptionStatus({
    required this.planType,
    required this.status,
    this.currentPeriodStart,
    this.currentPeriodEnd,
    required this.isActive,
    this.trialDaysRemaining = 0,
  });

  factory SubscriptionStatus.fromJson(Map<String, dynamic> json) {
    return SubscriptionStatus(
      planType: json['plan_type'] ?? 'free',
      status: json['status'] ?? 'active',
      currentPeriodStart: json['current_period_start'] != null
          ? DateTime.parse(json['current_period_start'])
          : null,
      currentPeriodEnd: json['current_period_end'] != null
          ? DateTime.parse(json['current_period_end'])
          : null,
      isActive: json['is_active'] ?? false,
      trialDaysRemaining: json['trial_days_remaining'] ?? 0,
    );
  }

  bool get isFree => planType == 'free';
  bool get isPersonal => planType == 'personal';
  bool get isFamily => planType == 'family';
  bool get isPaid => isPersonal || isFamily;
}

/// Available subscription plans
class SubscriptionPlans {
  static const personal = SubscriptionPlan(
    id: 'personal',
    name: '💪 个人强身计划',
    description: 'AI私教随时指导，动作准确不受伤',
    monthlyPrice: 9.99,
    yearlyPrice: 89.99,
    maxMembers: 1,
    features: [
      '✓ 全部20节课程（249分钟）',
      '✓ AI动作实时反馈（私教级指导）',
      '✓ 课程掌握追踪+成就徽章',
      '✓ 每日训练提醒养成习惯',
      '✓ 7天免费试用',
    ],
  );

  static const family = SubscriptionPlan(
    id: 'family',
    name: '🏆 家庭守护计划',
    description: '送父母一个私人教练+24小时健康守护',
    monthlyPrice: 14.99,
    yearlyPrice: 129.99,
    maxMembers: 4,
    features: [
      '✓ 全部20节课程 + AI动作实时反馈',
      '✓ 最多4人共享，全家一起练',
      '✓ 子女随时查看父母训练进度',
      '✓ 每日提醒养成锻炼习惯',
      '✓ 跌倒预防+平衡训练',
    ],
    isRecommended: true,
  );

  static List<SubscriptionPlan> get all => [personal, family];

  static SubscriptionPlan? getById(String id) {
    return all.where((p) => p.id == id).firstOrNull;
  }
}
