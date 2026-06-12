#!/usr/bin/env python3
"""
Update video URLs for courses and exercises.
Usage:
  python update_video_urls.py --course "椅子深蹲入门" --url "https://youtube.com/watch?v=XXX"
  python update_video_urls.py --course "椅子深蹲入门" --exercise "热身 - 关节活动" --url "https://youtube.com/watch?v=XXX"
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import get_settings

settings = get_settings()
sync_engine = create_engine(settings.SYNC_DATABASE_URL)

def update_course_video_url(course_title: str, video_url: str):
    with Session(sync_engine) as session:
        result = session.execute(
            text("SELECT id FROM courses WHERE title = :title"),
            {"title": course_title}
        )
        row = result.fetchone()
        if not row:
            print(f"Course not found: {course_title}")
            return False
        course_id = row[0]
        session.execute(
            text("UPDATE courses SET video_url = :url WHERE id = :id"),
            {"url": video_url, "id": str(course_id)}
        )
        session.commit()
        print(f"Updated course '{course_title}' (id={course_id}) with video_url: {video_url}")
        return True

def update_exercise_video_url(course_title: str, exercise_name: str, video_url: str):
    with Session(sync_engine) as session:
        result = session.execute(
            text("""
                SELECT e.id FROM exercises e
                JOIN courses c ON e.course_id = c.id
                WHERE c.title = :course_title AND e.name = :exercise_name
            """),
            {"course_title": course_title, "exercise_name": exercise_name}
        )
        row = result.fetchone()
        if not row:
            print(f"Exercise not found: {exercise_name} in course {course_title}")
            return False
        exercise_id = row[0]
        session.execute(
            text("UPDATE exercises SET video_url = :url WHERE id = :id"),
            {"url": video_url, "id": str(exercise_id)}
        )
        session.commit()
        print(f"Updated exercise '{exercise_name}' (id={exercise_id}) with video_url: {video_url}")
        return True

def list_courses():
    with Session(sync_engine) as session:
        result = session.execute(text("SELECT id, title, video_url FROM courses ORDER BY title"))
        print("\nCourses in database:")
        print(f"{'ID':<40} {'Title':<30} {'Video URL'}")
        print("-" * 90)
        for row in result:
            print(f"{str(row[0]):<40} {row[1]:<30} {row[2] or '(no video)'}")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update video URLs for courses/exercises")
    parser.add_argument("--course", help="Course title")
    parser.add_argument("--exercise", help="Exercise name (optional)")
    parser.add_argument("--url", help="YouTube video URL")
    parser.add_argument("--list", action="store_true", help="List all courses")
    args = parser.parse_args()

    if args.list:
        list_courses()
    elif args.course and args.url:
        if args.exercise:
            update_exercise_video_url(args.course, args.exercise, args.url)
        else:
            update_course_video_url(args.course, args.url)
    else:
        parser.print_help()