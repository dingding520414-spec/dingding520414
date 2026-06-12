class User {
  final String id;
  final String? email;
  final String? phone;
  final String name;
  final int? age;
  final String? gender;
  final String? fitnessGoal;
  final String? healthNotes;
  final String? avatarUrl;
  final DateTime createdAt;

  User({
    required this.id,
    this.email,
    this.phone,
    required this.name,
    this.age,
    this.gender,
    this.fitnessGoal,
    this.healthNotes,
    this.avatarUrl,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      phone: json['phone'],
      name: json['name'],
      age: json['age'],
      gender: json['gender'],
      fitnessGoal: json['fitness_goal'],
      healthNotes: json['health_notes'],
      avatarUrl: json['avatar_url'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'phone': phone,
      'name': name,
      'age': age,
      'gender': gender,
      'fitness_goal': fitnessGoal,
      'health_notes': healthNotes,
      'avatar_url': avatarUrl,
      'created_at': createdAt.toIso8601String(),
    };
  }
}