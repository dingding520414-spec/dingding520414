import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../core/theme/app_theme.dart';

class ProgressChart extends StatelessWidget {
  final List<dynamic> checkins;

  const ProgressChart({super.key, required this.checkins});

  @override
  Widget build(BuildContext context) {
    // Build last 7 days data
    final now = DateTime.now();
    final weekDays = List.generate(7, (index) {
      return now.subtract(Duration(days: 6 - index));
    });

    final weekDayLabels = ['一', '二', '三', '四', '五', '六', '日'];
    final todayWeekday = now.weekday;

    // Map checkins to bar data
    final barGroups = weekDays.asMap().entries.map((entry) {
      final index = entry.key;
      final day = entry.value;
      final hasCheckin = checkins.any((c) {
        final checkinDate = DateTime.parse(c['checkin_date']);
        return checkinDate.day == day.day &&
            checkinDate.month == day.month &&
            checkinDate.year == day.year;
      });

      return BarChartGroupData(
        x: index,
        barRods: [
          BarChartRodData(
            toY: hasCheckin ? 1 : 0,
            color: hasCheckin ? Colors.white : Colors.white30,
            width: 24,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(6)),
          ),
        ],
      );
    }).toList();

    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.spaceAround,
        maxY: 1,
        minY: 0,
        barTouchData: BarTouchData(enabled: false),
        titlesData: FlTitlesData(
          show: true,
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final dayIndex = (todayWeekday - 7 + value.toInt()) % 7;
                return Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Text(
                    weekDayLabels[dayIndex],
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 12,
                    ),
                  ),
                );
              },
            ),
          ),
          leftTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          topTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          rightTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
        ),
        gridData: const FlGridData(show: false),
        borderData: FlBorderData(show: false),
        barGroups: barGroups,
      ),
    );
  }
}