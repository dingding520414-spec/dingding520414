class Course {
  final String id;
  final String title;
  final String? description;
  final int difficulty;
  final int? durationMin;
  final String? videoUrl;
  final String? thumbnailUrl;
  final List<Exercise> exercises;

  Course({
    required this.id,
    required this.title,
    this.description,
    required this.difficulty,
    this.durationMin,
    this.videoUrl,
    this.thumbnailUrl,
    required this.exercises,
  });

  factory Course.fromJson(Map<String, dynamic> json) {
    return Course(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      difficulty: json['difficulty'],
      durationMin: json['duration_min'],
      videoUrl: json['video_url'],
      thumbnailUrl: json['thumbnail_url'],
      exercises: (json['exercises'] as List?)
              ?.map((e) => Exercise.fromJson(e))
              .toList() ??
          [],
    );
  }

  String get difficultyStars => '★' * difficulty + '☆' * (5 - difficulty);
}

class Exercise {
  final String id;
  final String name;
  final String? description;
  final int? reps;
  final int? durationSec;
  final int? videoTimestamp;
  final int orderIndex;

  Exercise({
    required this.id,
    required this.name,
    this.description,
    this.reps,
    this.durationSec,
    this.videoTimestamp,
    required this.orderIndex,
  });

  factory Exercise.fromJson(Map<String, dynamic> json) {
    return Exercise(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      reps: json['reps'],
      durationSec: json['duration_sec'],
      videoTimestamp: json['video_timestamp'],
      orderIndex: json['order_index'],
    );
  }
}