#!/usr/bin/env python3
"""
Video #01 Assembly Script - 5分钟椅子腿部训练
用 Pillow 渲染文字到图片，再用 FFmpeg 生成视频
"""

import imageio_ffmpeg
import subprocess
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import tempfile

PROJECT_DIR = Path("/home/admin1234/.openclaw/workspace/projects/senior-strength-app/video-production/01_chair_leg_training")
OUTPUT_FILE = PROJECT_DIR / "output_01_chair_leg_training.mp4"
BGM_FILE = PROJECT_DIR / "bgm.mp3"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

WIDTH = 1280
HEIGHT = 720
FPS = 25

# 场景定义: (图片文件, 显示秒数, 标题, 副标题)
scenes = [
    ("cover.png",              8,  "5-Minute Chair Leg Training",            "Strength Training for Seniors | Ageless Strength"),
    ("scene4_knee_pain.png",  20,  "Knee Discomfort? It Might Be Muscle Weakness", "Many seniors experience knee pain due to weakened leg muscles"),
    ("scene1_chair_squat.png", 35,  "Step 1: The Chair Squat",                "Stand in front of chair, arms forward, slowly lower until you touch the seat"),
    ("scene2_seated_leg_raise.png", 35, "Step 2: Seated Leg Raise",          "Sit straight, extend one leg, hold for 3 seconds, alternate legs"),
    ("scene3_form_check.png",  30,  "Form Check - Do It Right!",             "Keep your back straight | Knees over toes | Core engaged"),
    ("scene5_ai_feedback.png", 30,  "AI Real-Time Pose Detection",           "Get instant feedback on your form - just like having a personal trainer"),
    ("scene7_app_ui.png",      25,  "Try Ageless Strength App",              "AI Pose Detection | Personalized Plans | Family Sharing"),
    ("scene6_cta.png",          15,  "Start Your 7-Day Free Trial Today",    "Ageless Strength - Strength Training for Every Age"),
]

def get_font(size):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def render_scene(img_path, title, subtitle):
    """把标题和副标题渲染到图片上"""
    # 加载原图，缩放裁剪到 1280x720
    img = Image.open(img_path).convert("RGB")
    scale = max(WIDTH / img.width, HEIGHT / img.height)
    new_w = int(img.width * scale)
    new_h = int(img.height * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - WIDTH) // 2
    top = (new_h - HEIGHT) // 2
    img = img.crop((left, top, left + WIDTH, top + HEIGHT))

    # 底部渐变遮罩
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(HEIGHT - 180, HEIGHT):
        alpha = int(200 * (y - (HEIGHT - 180)) / 180)
        draw.rectangle([(0, y), (WIDTH, y + 1)], fill=(0, 0, 0, alpha))

    img = Image.alpha_composite(img.convert("RGBA"), overlay)

    # 标题
    draw = ImageDraw.Draw(img)
    font_title = get_font(42)
    font_sub = get_font(26)
    # 标题
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, HEIGHT - 140), title, font=font_title, fill="white")
    # 副标题
    bbox2 = draw.textbbox((0, 0), subtitle, font=font_sub)
    sw = bbox2[2] - bbox2[0]
    draw.text(((WIDTH - sw) // 2, HEIGHT - 85), subtitle, font=font_sub, fill=(200, 200, 200, 255))

    return img.convert("RGB")

def build():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        # 生成所有带文字的场景图片
        print("🖼️  渲染场景图片...")
        scene_files = []
        total_dur = 0
        for i, (img_file, dur, title, sub) in enumerate(scenes):
            out = tmppath / f"scene_{i:02d}.jpg"
            img_path = PROJECT_DIR / img_file
            rendered = render_scene(img_path, title, sub)
            rendered.save(out, "JPEG", quality=92)
            scene_files.append((out, dur))
            total_dur += dur
            print(f"  场景 {i+1}/{len(scenes)}: {img_file} → {dur}s")

        # 用 FFmpeg concat 生成视频
        # 先为每个场景生成独立的视频片段
        print("🎬 生成视频片段...")
        clip_files = []
        for i, (img_file, dur) in enumerate(scene_files):
            clip_file = tmppath / f"clip_{i:02d}.mp4"
            cmd = [
                str(FFMPEG), "-y",
                "-loop", "1", "-i", str(img_file),
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-t", str(dur), "-r", str(FPS),
                "-frames:v", str(dur * FPS),
                str(clip_file)
            ]
            # 简化：直接生成固定帧数的视频
            cmd = [
                str(FFMPEG), "-y",
                "-loop", "1", "-i", str(img_file),
                "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},fps={FPS}",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-t", str(dur),
                str(clip_file)
            ]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                print(f"❌ clip {i} 失败: {r.stderr[-500:]}")
                return
            clip_files.append(str(clip_file))
            print(f"  片段 {i+1}/{len(scenes)} 完成 ({dur}s)")

        # 拼接所有片段
        concat_list = tmppath / "concat.txt"
        with open(concat_list, "w") as f:
            for cf in clip_files:
                f.write(f"file '{cf}'\n")

        video_only = tmppath / "video_only.mp4"
        cmd = [
            str(FFMPEG), "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-pix_fmt", "yuv420p",
            str(video_only)
        ]
        print("✂️  拼接所有片段...")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"❌ 拼接失败: {r.stderr[-500:]}")
            return

        # 添加音频
        print("🎵 合并背景音乐...")
        cmd = [
            str(FFMPEG), "-y",
            "-i", str(video_only),
            "-i", str(BGM_FILE),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(OUTPUT_FILE)
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"❌ 音频合并失败: {r.stderr[-500:]}")
            return

    size_mb = os.path.getsize(OUTPUT_FILE) / 1024 / 1024
    print(f"\n🎉 成品视频生成完成!")
    print(f"📁 {OUTPUT_FILE}")
    print(f"⏱️  时长: {total_dur}s ({total_dur/60:.1f}分钟)")
    print(f"📦 大小: {size_mb:.1f} MB")

if __name__ == "__main__":
    print("=" * 50)
    print("🎬 Video #01 Assembly - Chair Leg Training")
    print("=" * 50)
    build()
