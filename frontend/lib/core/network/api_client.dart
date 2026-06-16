import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

class ApiClient {
  static const String baseUrl = 'http://localhost:8000/api/v1';
  
  late final Dio _dio;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  ApiClient() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(key: 'access_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        if (error.response?.statusCode == 401) {
          // Token expired, try to refresh
          _handleUnauthorized();
        }
        return handler.next(error);
      },
    ));
  }

  Future<void> _handleUnauthorized() async {
    // Clear tokens and redirect to login
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
  }

  // Auth
  Future<Map<String, dynamic>> register({
    String? email,
    String? phone,
    required String password,
    required String name,
    int? age,
    String role = 'elder',
  }) async {
    final response = await _dio.post('/auth/register', data: {
      if (email != null) 'email': email,
      if (phone != null) 'phone': phone,
      'password': password,
      'name': name,
      if (age != null) 'age': age,
      'role': role,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> login({
    String? email,
    String? phone,
    required String password,
  }) async {
    final response = await _dio.post('/auth/login', data: {
      if (email != null) 'email': email,
      if (phone != null) 'phone': phone,
      'password': password,
    });
    return response.data;
  }

  Future<void> saveTokens(String accessToken, String refreshToken) async {
    await _storage.write(key: 'access_token', value: accessToken);
    await _storage.write(key: 'refresh_token', value: refreshToken);
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
  }

  Future<String?> getAccessToken() async {
    return await _storage.read(key: 'access_token');
  }

  // User
  Future<Map<String, dynamic>> getCurrentUser() async {
    final response = await _dio.get('/users/me');
    return response.data;
  }

  Future<Map<String, dynamic>> updateUser(Map<String, dynamic> data) async {
    final response = await _dio.patch('/users/me', data: data);
    return response.data;
  }

  // Courses
  Future<List<Map<String, dynamic>>> getCourses({
    int? difficulty,
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _dio.get('/courses', queryParameters: {
      if (difficulty != null) 'difficulty': difficulty,
      'limit': limit,
      'offset': offset,
    });
    return response.data['courses'];
  }

  Future<Map<String, dynamic>> getCourse(String courseId) async {
    final response = await _dio.get('/courses/$courseId');
    return response.data;
  }

  // Training
  Future<Map<String, dynamic>> startTraining(String courseId) async {
    final response = await _dio.post('/training/start', data: {
      'course_id': courseId,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> completeTraining(
    String sessionId, {
    required int durationSec,
    int? aiScore,
  }) async {
    final response = await _dio.post('/training/$sessionId/complete', data: {
      'duration_sec': durationSec,
      if (aiScore != null) 'ai_score': aiScore,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> getAIFeedback(
    String sessionId,
    String exerciseId, {
    String? videoSegmentBase64,
  }) async {
    final response = await _dio.post('/training/$sessionId/ai-feedback', data: {
      'exercise_id': exerciseId,
      if (videoSegmentBase64 != null)
        'video_segment_base64': videoSegmentBase64,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> getWeeklyProgress({String? userId}) async {
    final response = await _dio.get('/training/progress/weekly', queryParameters: {
      if (userId != null) 'user_id': userId,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> getMonthlyReport({
    String? userId,
    int? month,
  }) async {
    final response = await _dio.get('/training/progress/monthly', queryParameters: {
      if (userId != null) 'user_id': userId,
      if (month != null) 'month': month,
    });
    return response.data;
  }

  // Family
  Future<Map<String, dynamic>> generateBindCode() async {
    final response = await _dio.post('/family/generate-code');
    return response.data;
  }

  Future<List<Map<String, dynamic>>> bindToFamily(String bindCode) async {
    final response = await _dio.post('/family/bind', data: {
      'bind_code': bindCode,
    });
    return response.data;
  }

  Future<List<Map<String, dynamic>>> getFamilyMembers() async {
    final response = await _dio.get('/family/members');
    return response.data;
  }

  Future<Map<String, dynamic>> getElderProgress(String elderId) async {
    final response = await _dio.get('/family/progress/$elderId');
    return response.data;
  }

  // Subscription
  Future<Map<String, dynamic>> createSubscription(String planType, {String interval = 'month'}) async {
    final response = await _dio.post('/subscription/create', data: {
      'plan_type': planType,
      'interval': interval,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> cancelSubscription() async {
    final response = await _dio.post('/subscription/cancel');
    return response.data;
  }

  Future<Map<String, dynamic>> getSubscriptionStatus() async {
    final response = await _dio.get('/subscription/status');
    return response.data;
  }
}