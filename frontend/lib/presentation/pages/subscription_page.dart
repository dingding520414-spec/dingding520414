import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/subscription.dart';
import '../providers/subscription_provider.dart';

class SubscriptionPage extends ConsumerStatefulWidget {
  const SubscriptionPage({super.key});

  @override
  ConsumerState<SubscriptionPage> createState() => _SubscriptionPageState();
}

class _SubscriptionPageState extends ConsumerState<SubscriptionPage> {
  @override
  void initState() {
    super.initState();
    // Load subscription status when page opens
    Future.microtask(() {
      ref.read(subscriptionProvider.notifier).loadStatus();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(subscriptionProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('订阅计划'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: state.isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Current Status Banner
                  if (state.status != null && state.status!.isPaid)
                    _buildCurrentPlanBanner(state.status!)
                  else if (state.status != null && state.status!.trialDaysRemaining > 0)
                    _buildTrialBanner(state.status!.trialDaysRemaining),

                  const SizedBox(height: 24),

                  // Pricing Header
                  const Text(
                    '选择您的计划',
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '解锁全部课程和高级功能',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 24),

                  // Monthly/Yearly Toggle
                  _buildPricingToggle(state),
                  const SizedBox(height: 24),

                  // Plan Cards
                  _buildPlanCards(state),
                  const SizedBox(height: 24),

                  // FAQ Section
                  _buildFAQSection(),
                  const SizedBox(height: 32),
                ],
              ),
            ),
    );
  }

  Widget _buildCurrentPlanBanner(SubscriptionStatus status) {
    final plan = SubscriptionPlans.getById(status.planType);
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.green.shade200),
      ),
      child: Row(
        children: [
          Icon(Icons.check_circle, color: Colors.green.shade700, size: 32),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '当前计划: ${plan?.name ?? status.planType}',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.green.shade700,
                  ),
                ),
                if (status.currentPeriodEnd != null)
                  Text(
                    '有效期至: ${_formatDate(status.currentPeriodEnd!)}',
                    style: TextStyle(color: Colors.green.shade600, fontSize: 13),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTrialBanner(int daysRemaining) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.orange.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.orange.shade200),
      ),
      child: Row(
        children: [
          Icon(Icons.access_time, color: Colors.orange.shade700, size: 32),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '免费试用中',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.orange.shade700,
                  ),
                ),
                Text(
                  '剩余 $daysRemaining 天 • 之后将自动转为付费订阅',
                  style: TextStyle(color: Colors.orange.shade600, fontSize: 13),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPricingToggle(SubscriptionState state) {
    return Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: Colors.grey.shade200,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Expanded(
            child: GestureDetector(
              onTap: () => ref.read(subscriptionProvider.notifier).setSelectedTab(0),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: state.selectedTab == 0 ? Colors.white : Colors.transparent,
                  borderRadius: BorderRadius.circular(8),
                  boxShadow: state.selectedTab == 0
                      ? [BoxShadow(color: Colors.black.withAlpha(25))]
                      : null,
                ),
                child: Text(
                  '月付',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: state.selectedTab == 0 ? Colors.black : Colors.grey,
                  ),
                ),
              ),
            ),
          ),
          Expanded(
            child: GestureDetector(
              onTap: () => ref.read(subscriptionProvider.notifier).setSelectedTab(1),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: state.selectedTab == 1 ? Colors.white : Colors.transparent,
                  borderRadius: BorderRadius.circular(8),
                  boxShadow: state.selectedTab == 1
                      ? [BoxShadow(color: Colors.black.withAlpha(25))]
                      : null,
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      '年付',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: state.selectedTab == 1 ? Colors.black : Colors.grey,
                      ),
                    ),
                    if (state.selectedTab == 1) ...[
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.red,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Text(
                          '省25%',
                          style: TextStyle(color: Colors.white, fontSize: 11),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPlanCards(SubscriptionState state) {
    final isYearly = state.selectedTab == 1;

    return Column(
      children: SubscriptionPlans.all.map((plan) {
        return _buildPlanCard(plan, isYearly, state);
      }).toList(),
    );
  }

  Widget _buildPlanCard(SubscriptionPlan plan, bool isYearly, SubscriptionState state) {
    final price = isYearly ? plan.yearlyPrice : plan.monthlyPrice;
    final pricePeriod = isYearly ? '/年' : '/月';
    final originalPrice = isYearly ? plan.monthlyPrice * 12 : null;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: plan.isRecommended ? Colors.blue : Colors.grey.shade300,
          width: plan.isRecommended ? 2 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(13),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          // Recommended Badge
          if (plan.isRecommended)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 8),
              decoration: BoxDecoration(
                color: Colors.blue,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(14),
                  topRight: Radius.circular(14),
                ),
              ),
              child: const Text(
                '⭐ 推荐',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),

          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Plan Name & Price
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          plan.name,
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          plan.description,
                          style: TextStyle(
                            color: Colors.grey.shade600,
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          '\$${price.toStringAsFixed(2)}',
                          style: const TextStyle(
                            fontSize: 32,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          pricePeriod,
                          style: TextStyle(color: Colors.grey.shade600),
                        ),
                      ],
                    ),
                  ],
                ),
                if (originalPrice != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    '原价 \$${originalPrice.toStringAsFixed(2)}',
                    style: TextStyle(
                      color: Colors.grey.shade500,
                      decoration: TextDecoration.lineThrough,
                      fontSize: 13,
                    ),
                  ),
                ],

                const SizedBox(height: 16),
                const Divider(),
                const SizedBox(height: 12),

                // Features
                ...plan.features.map((feature) => Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        children: [
                          Icon(
                            Icons.check,
                            color: Colors.green.shade600,
                            size: 20,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            feature.replaceFirst('✓ ', ''),
                            style: const TextStyle(fontSize: 14),
                          ),
                        ],
                      ),
                    )),

                const SizedBox(height: 16),

                // Subscribe Button
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: state.isLoading
                        ? null
                        : () => _onSubscribe(plan.id, isYearly ? 'year' : 'month'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: plan.isRecommended ? Colors.blue : Colors.black,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Text(
                      state.isLoading ? '处理中...' : '立即订阅',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),

                // 7-day free trial note
                const SizedBox(height: 8),
                Text(
                  '前7天免费试用，不满意可取消',
                  style: TextStyle(
                    color: Colors.grey.shade500,
                    fontSize: 12,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFAQSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          '常见问题',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        _buildFAQItem(
          '如何取消订阅？',
          '您可以随时在个人中心取消订阅，取消后仍可使用剩余订阅期限。',
        ),
        _buildFAQItem(
          '7天免费试用如何工作？',
          '首次订阅可享受7天免费试用，试用期内可随时取消且不收取费用。',
        ),
        _buildFAQItem(
          '家庭计划如何添加成员？',
          '订阅家庭计划后，您可以通过家庭邀请码最多添加3位家庭成员。',
        ),
        _buildFAQItem(
          '订阅后可以切换计划吗？',
          '可以，您可以在订阅期间切换个人计划和家庭计划。',
        ),
      ],
    );
  }

  Widget _buildFAQItem(String question, String answer) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(12),
      ),
      child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 16),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        title: Text(
          question,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        children: [
          Text(
            answer,
            style: TextStyle(color: Colors.grey.shade700),
          ),
        ],
      ),
    );
  }

  void _onSubscribe(String planType, String interval) {
    // TODO: Implement actual Stripe checkout
    ref.read(subscriptionProvider.notifier).subscribe(planType, interval);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('正在跳转到支付页面...'),
        backgroundColor: Colors.blue,
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }
}
