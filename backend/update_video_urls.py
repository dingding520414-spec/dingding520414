"""
更新课程视频URL
视频文件已保存到 videos/ 目录
"""
import os
import sqlite3

VIDEO_DIR = "/home/admin1234/.openclaw/workspace/projects/senior-strength-app/videos"

# 视频文件映射到课程ID
# 格式: course_id: video_filename
COURSE_VIDEOS = {
    1: "01_chair_squat.mp4",           # 椅子深蹲入门
    2: "02_wall_pushup.mp4",           # 墙壁俯卧撑
    3: "06_resistance_band_fullbody.mp4",  # 弹力带全身组合 (复用)
    4: "06_resistance_band_fullbody.mp4",  # 弹力带腿部训练 (复用)
    5: "03_seated_leg.mp4",            # 坐姿腿举训练
    6: "dumbbell_lateral.mp4",         # 哑铃入门 (待生成)
    7: "04_bodyweight_squat.mp4",      # 自重深蹲基础
    8: "05_wall_pushup_advanced.mp4",  # 墙壁俯卧撑进阶
    9: "06_resistance_band_fullbody.mp4",  # 弹力带全身组合
    10: "balance_stability.mp4",        # 平衡与稳定训练 (待生成)
}

def update_video_urls():
    db_path = "/home/admin1234/.openclaw/workspace/projects/senior-strength-app/backend/senior_strength.db"
    
    if not os.path.exists(db_path):
        print(f"数据库不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='courses'")
    if not cursor.fetchone():
        print("数据库中没有 courses 表")
        conn.close()
        return
    
    updated = 0
    for course_id, video_file in COURSE_VIDEOS.items():
        video_path = os.path.join(VIDEO_DIR, video_file)
        if os.path.exists(video_path):
            # 使用 file:// URL
            video_url = f"file://{video_path}"
            cursor.execute("UPDATE courses SET video_url = ? WHERE id = ?", (video_url, course_id))
            updated += 1
            print(f"Updated course {course_id}: {video_file}")
        else:
            print(f"Video not found for course {course_id}: {video_path}")
    
    conn.commit()
    print(f"\n✅ 成功更新 {updated} 个课程的视频URL")
    conn.close()

if __name__ == "__main__":
    update_video_urls()
