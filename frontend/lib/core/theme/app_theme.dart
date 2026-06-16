import 'package:flutter/material.dart';

class AppColors {
  // Primary
  static const Color primary = Color(0xFF2563EB);
  static const Color primaryDark = Color(0xFF1D4ED8);
  static const Color primaryLight = Color(0xFF93C5FD);

  // Secondary
  static const Color secondary = Color(0xFF10B981);
  static const Color secondaryDark = Color(0xFF059669);
  static const Color secondaryLight = Color(0xFF6EE7B7);

  // Neutral
  static const Color background = Color(0xFFF8FAFC);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color textPrimary = Color(0xFF1E293B);
  static const Color textSecondary = Color(0xFF64748B);
  static const Color textTertiary = Color(0xFF94A3B8);

  // Semantic
  static const Color success = Color(0xFF22C55E);
  static const Color warning = Color(0xFFF59E0B);
  static const Color error = Color(0xFFEF4444);
  static const Color info = Color(0xFF3B82F6);

  // Elder-specific
  static const Color elderAccent = Color(0xFF8B5CF6);
  static const Color streakFlame = Color(0xFFFB923C);
}

class AppTheme {
  static TextStyle _textStyle({
    double fontSize = 16,
    FontWeight fontWeight = FontWeight.normal,
    Color? color,
  }) {
    return TextStyle(
      fontSize: fontSize,
      fontWeight: fontWeight,
      color: color ?? AppColors.textPrimary,
    );
  }

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: ColorScheme.light(
        primary: AppColors.primary,
        secondary: AppColors.secondary,
        surface: AppColors.surface,
        error: AppColors.error,
      ),
      scaffoldBackgroundColor: AppColors.background,
      textTheme: TextTheme(
        displayLarge: _textStyle(fontSize: 32, fontWeight: FontWeight.bold),
        displayMedium: _textStyle(fontSize: 28, fontWeight: FontWeight.bold),
        displaySmall: _textStyle(fontSize: 24, fontWeight: FontWeight.bold),
        headlineLarge: _textStyle(fontSize: 22, fontWeight: FontWeight.w600),
        headlineMedium: _textStyle(fontSize: 20, fontWeight: FontWeight.w600),
        headlineSmall: _textStyle(fontSize: 18, fontWeight: FontWeight.w600),
        bodyLarge: _textStyle(fontSize: 18),
        bodyMedium: _textStyle(fontSize: 16),
        bodySmall: _textStyle(fontSize: 14, color: AppColors.textSecondary),
        labelLarge: _textStyle(fontSize: 16, fontWeight: FontWeight.w600),
      ),
      appBarTheme: AppBarTheme(
        elevation: 0,
        centerTitle: true,
        backgroundColor: AppColors.surface,
        foregroundColor: AppColors.textPrimary,
        titleTextStyle: _textStyle(fontSize: 20, fontWeight: FontWeight.w600),
      ),
      cardTheme: CardThemeData(
        elevation: 2,
        shadowColor: AppColors.textTertiary.withOpacity(0.1),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: _textStyle(fontSize: 18, fontWeight: FontWeight.w600),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.primary,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          side: const BorderSide(color: AppColors.primary, width: 2),
          textStyle: _textStyle(fontSize: 18, fontWeight: FontWeight.w600),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.surface,
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: AppColors.textTertiary),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: AppColors.textTertiary.withOpacity(0.5)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.error),
        ),
        labelStyle: _textStyle(fontSize: 16, color: AppColors.textSecondary),
      ),
    );
  }
}