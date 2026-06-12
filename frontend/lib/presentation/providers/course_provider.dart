import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../../data/models/course.dart';

final coursesProvider =
    FutureProvider.family<List<Course>, int?>((ref, difficulty) async {
  final apiClient = ref.read(apiClientProvider);
  final courses = await apiClient.getCourses(difficulty: difficulty);
  return courses.map((c) => Course.fromJson(c)).toList();
});

final courseDetailProvider =
    FutureProvider.family<Course, String>((ref, courseId) async {
  final apiClient = ref.read(apiClientProvider);
  final course = await apiClient.getCourse(courseId);
  return Course.fromJson(course);
});