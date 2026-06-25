#!/usr/bin/env python3
"""
批量组装所有9个视频
使用已有图片素材 + 新生成的音乐
"""

import imageio_ffmpeg
import subprocess
import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import tempfile

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
WIDTH, HEIGHT = 1280, 720
FPS = 25
MEDIA_IMG = Path("/home/admin1234/.openclaw/media/tool-image-generation")
MEDIA_MUSIC = Path("/home/admin1234/.openclaw/media/tool-music-generation")
PROJECT_BASE = Path("/home/admin1234/.openclaw/workspace/projects/senior-strength-app/video-production")
TRACK = MEDIA_MUSIC / "track-1---5a2e971e-7c46-4a0f-a48a-9fb3db703b6e.mp3"  # 通用背景音乐

def get_font(size=36):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def resize_crop(img_path):
    img = Image.open(img_path).convert("RGB")
    scale = max(WIDTH / img.width, HEIGHT / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    l = (nw - WIDTH) // 2
    t = (nh - HEIGHT) // 2
    return img.crop((l, t, l + WIDTH, t + HEIGHT))

def render_scene(img_path, title, subtitle):
    img = resize_crop(img_path)
    ov = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ov)
    for y in range(HEIGHT - 180, HEIGHT):
        alpha = int(210 * (y - (HEIGHT - 180)) / 180)
        draw.rectangle([(0, y), (WIDTH, y + 1)], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), ov)
    draw = ImageDraw.Draw(img)
    ft, fs = get_font(42), get_font(26)
    # title
    bbox = draw.textbbox((0, 0), title, font=ft)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, HEIGHT - 140), title, font=ft, fill="white")
    # subtitle
    bbox2 = draw.textbbox((0, 0), subtitle, font=fs)
    sw = bbox2[2] - bbox2[0]
    draw.text(((WIDTH - sw) // 2, HEIGHT - 85), subtitle, font=fs, fill=(200, 200, 200))
    return img.convert("RGB")

# ============================================================
# 视频定义：(目录名, 主题描述, [(图片ID, 显示秒数, 标题, 副标题), ...])
# 图片ID不带时间戳后缀，自动找最新文件
# ============================================================

def find_img(keyword):
    """根据关键词找最新的图片文件"""
    files = sorted(MEDIA_IMG.glob(f"image-1---{keyword}*.png"))
    if files:
        return str(files[-1])
    # fallback: 找包含keyword的文件
    all_files = sorted(MEDIA_IMG.glob("image-1---*.png"), key=os.path.getmtime, reverse=True)
    for f in all_files:
        if keyword.lower() in f.stem.lower():
            return str(f)
    return None

# 视频2: 弹力带全身训练
VIDEO_02_SCENES = [
    ("aaa4038a",  8,  "Resistance Band Full Body Training", "Strength Training for Seniors | Ageless Strength"),
    ("c14beda1", 30,  "Step 1: Bicep Curl", "Keep elbows at your sides, squeeze at the top"),
    ("5ac33004",  30,  "Personalized Plan Just For You", "Get a resistance band set matched to your fitness level"),
    ("293cbed8",  35,  "Step 2: Leg Curl with Band", "Stand on one leg, curl the other back slowly"),
    ("fcb14201",  35,  "Step 3: Seated Row", "Pull the band toward your belly button"),
    ("76dbd5d4",  30,  "Step 4: Band Squat", "Feet shoulder-width, sit back like in a chair"),
    ("3a4c12c2",  20,  "Try Ageless Strength - AI Pose Detection", "Get instant feedback on every rep you do"),
    ("0152c1ae",  15,  "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]

# 视频3: 坐姿哑铃肩部训练
VIDEO_03_SCENES = [
    ("1d2c0ac2",  8,  "Seated Dumbbell Shoulder Training", "Strength Training for Seniors | Ageless Strength"),
    ("d92ef8f3",  35,  "Step 1: Seated Shoulder Press", "Press weights straight up, control the descent"),
    ("81ea2f1d",  30,  "Share Your Progress with Family", "Invite family members to follow your fitness journey"),
    ("9ae90bc0",  30,  "Family Dashboard - See Everyone's Progress", "One subscription, the whole family stays connected"),
    ("e25c6059",  35,  "Step 2: Lateral Raise", "Raise arms out to sides, slight bend in elbows"),
    ("8a6a64cf",  35,  "Step 3: Front Raise", "Alternate arms, control the movement"),
    ("3c0fadae",  25,  "AI Real-Time Form Feedback", "Your phone watches your form - just like a personal trainer"),
    ("0152c1ae",  15,  "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]

# 视频4: 平衡力防摔倒
VIDEO_04_SCENES = [
    ("5aa7934e",  8,  "Balance Training - Prevent Falls", "Strength Training for Seniors | Ageless Strength"),
    ("d36b8c82",  25,  "Falls Are the #1 Threat to Senior Health", "But they're preventable with the right training"),
    ("af9d3d8e",  35,  "Step 1: Tandem Stance", "Stand heel to toe, like on a tightrope"),
    ("083690a1",  35,  "Step 2: Single Leg Stance", "Hold for 30 seconds each leg - don't forget to breathe"),
    ("1e43f2dd",  30,  "Family Guardian - Stay Connected", "Your family gets notified if something seems wrong"),
    ("686c5b20",  30,  "AI Motion Detection - Real-Time Safety", "Get alerted if your balance wavers during exercise"),
    ("8555f6e9",  30,  "Try Ageless Strength - Track Your Balance Progress", "See your improvement week by week"),
    ("0152c1ae",  15,  "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]

# 视频5: 核心稳定零基础版
VIDEO_05_SCENES = [
    ("54ba8535",  8,  "Core Stability Training - Zero Equipment", "Strength Training for Seniors | Ageless Strength"),
    ("64b05d0d",  35,  "Step 1: Bird Dog", "Extend opposite arm and leg, keep back flat"),
    ("b296fee4",  30,  "Core Stability - Control is Everything", "Slow and controlled beats fast and sloppy"),
    ("a1073ef7",  30,  "Track Your Progress Over Time", "See your improvement in core strength and stability"),
    ("68c7fe35",  35,  "Step 2: Seated Core Tighten", "Sit tall, pull navel toward spine, hold and breathe"),
    ("37a452ab",  35,  "Step 3: Leg Extension", "Extend one leg at a time, keep core engaged"),
    ("347b862e",  25,  "Progress Tracking - Celebrate Every Win", "Ageless Strength tracks your improvements automatically"),
    ("0152c1ae",  15,  "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]

# 视频6: 阻力带腿部塑形
VIDEO_06_SCENES = [
    ("76db883b",  8,  "Resistance Band Leg Training", "Strength Training for Seniors | Ageless Strength"),
    ("e25c6059",  35,  "Step 1: Lateral Leg Raise", "Lift leg out to side, slow and controlled"),
    ("76dbd5d4",  35,  "Step 2: Band Squat", "Sit back into the squat, keep knees behind toes"),
    ("fcb14201",  35,  "Step 3: Standing Hamstring Curl", "Curl heel toward glutes, squeeze at the top"),
    ("293cbed8",  30,  "Step 4: Leg Extension", "Strengthen your quadriceps from a seated position"),
    ("c7d698ad",  30,  "Step 5: Hip Bridge", "Lie on back, lift hips, hold at the top"),
    ("7a76ccc8",  25,  "Premium Content - Unlock All 20+ Courses", "Subscribe to access every training program"),
    ("0152c1ae",  15,  "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]

# 视频7: 早晚拉伸完整版
VIDEO_07_SCENES = [
    ("0c6f6963",  8,  "Complete Morning & Evening Stretch", "Strength Training for Seniors | Ageless Strength"),
    ("68c7fe35",  30,  "Step 1: Seated Hamstring Stretch", "Extend one leg, lean forward slightly, hold 30 seconds"),
    ("d524b028",  30,  "Step 2: Standing Quad Stretch", "Hold ankle behind you, keep knees together"),
    ("c7d698ad",  30,  "Step 3: Hip Flexor Lunge", "Lunge forward, drop back knee toward floor"),
    ("b015ac73",  30,  "Step 4: Neck & Shoulder Release", "Gentle head tilts and shoulder rolls"),
    ("dc8f5378",  30,  "Step 5: Spinal Twist", "Rotate torso, look over each shoulder"),
    ("37a452ab",  25,  "Daily Reminders - Build Your Habit", "Set workout reminders and never miss a day"),
    ("0152c1ae",  15,  "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]

# 视频8: 椅子深蹲正确姿势
VIDEO_08_SCENES = [
    ("037bb945",  8,  "Chair Squat - Perfect Your Form", "Strength Training for Seniors | Ageless Strength"),
    ("18b101f6",  30,  "Why Chair Squats Matter", "They mimic the motion of sitting down and standing up"),
    ("76dbd5d4",  35,  "Step 1: Stand in Front of Chair", "Feet shoulder-width, toes slightly turned out"),
    ("430568d5",  35,  "Step 2: The Descent", "Push hips back, bend knees, lower until you touch the seat"),
    ("916b2d14",  30,  "The #1 Mistake: Knees Past Toes", "Keep your weight in your heels, knees over toes"),
    ("8555f6e9",  30,  "AI Real-Time Form Correction", "Your phone detects your form and gives instant tips"),
    ("7cfdb1ac",  25,  "Try the AI Pose Detection Feature", "Just like having a personal trainer watching your every rep"),
    ("0152c1ae",  15,  "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]

# 视频9: 力量训练常见误区
VIDEO_09_SCENES = [
    ("6fd503bd",  8,  "5 Common Strength Training Mistakes", "Strength Training for Seniors | Ageless Strength"),
    ("639c0ca1",  30,  "Mistake #1: Holding Your Breath", "Breathe normally - exhale during effort, inhale on recovery"),
    ("a3dc86fa",  30,  "Mistake #2: Working Through Pain", "Pain is your body's warning signal - respect it!"),
    ("e7222044",  30,  "Mistake #3: Too Much Too Soon", "Quality over quantity - build gradually"),
    ("775fe408",  30,  "Mistake #4: Skipping Warm-Up", "Cold muscles are injury-prone - always warm up first"),
    ("df6b8cec",  30,  "Mistake #5: No Rest Days", "Your muscles grow during rest, not during exercise"),
    ("7a76ccc8",  25,  "Learn the Science of Strength Training", "Ageless Strength - built on proper exercise science"),
    ("0152c1ae",  15,  "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]

# 视频10: 家庭训练计划
VIDEO_10_SCENES = [
    ("179ee92b",  8,  "Design Your Family Workout Plan", "Strength Training for Seniors | Ageless Strength"),
    ("a0eb002f",  30,  "One Subscription, Whole Family", "Share your progress and hold each other accountable"),
    ("f7022b71",  30,  "Individual vs Family Plan", "Family plan at $14.99/mo = best value for your household"),
    ("2667fb76",  35,  "Set Weekly Goals Together", "Plan workouts as a family - consistency is everything"),
    ("a1073ef7",  35,  "Track Every Family Member's Progress", "Watch mom, dad, and yourself improve week by week"),
    ("347b862e",  30,  "Stay Motivated as a Family", "When one person trains, the whole family cheers them on"),
    ("a0eb002f",  25,  "20+ Exercise Courses Included", "From beginner to advanced - something for every fitness level"),
    ("0152c1ae",  15,  "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]

ALL_VIDEOS = [
    ("02_resistance_band_fullbody",    VIDEO_02_SCENES),
    ("03_seated_dumbbell_shoulder",    VIDEO_03_SCENES),
    ("04_balance_fall_prevention",      VIDEO_04_SCENES),
    ("05_core_stability",              VIDEO_05_SCENES),
    ("06_resistance_band_legs",        VIDEO_06_SCENES),
    ("07_morning_evening_stretch",     VIDEO_07_SCENES),
    ("08_chair_squat_form",            VIDEO_08_SCENES),
    ("09_strength_mistakes",            VIDEO_09_SCENES),
    ("10_family_workout_plan",          VIDEO_10_SCENES),
]

def find_image(keyword):
    """Find most recent image matching keyword"""
    all_files = sorted(MEDIA_IMG.glob("image-1---*.png"), key=os.path.getmtime, reverse=True)
    kw = keyword.lower()
    for f in all_files:
        if kw in f.stem.lower():
            return str(f)
    return None

def assemble_video(dir_name, scenes):
    """Assemble a single video from scene definitions"""
    proj_dir = PROJECT_BASE / dir_name
    proj_dir.mkdir(exist_ok=True)
    
    # Find music - try to find a dedicated track
    music_files = sorted(MEDIA_MUSIC.glob("*.mp3"), key=os.path.getmtime, reverse=True)
    music_file = str(music_files[0]) if music_files else str(TRACK)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        print(f"🖼️  渲染场景...")
        scene_files = []
        total_dur = 0
        for i, (img_id, dur, title, subtitle) in enumerate(scenes):
            img_path = find_image(img_id)
            if img_path:
                rendered = render_scene(img_path, title, subtitle)
                out = tmp / f"scene_{i:02d}.jpg"
                rendered.save(out, "JPEG", quality=90)
                scene_files.append((str(out), dur))
                print(f"  场景 {i+1}/{len(scenes)}: ✅ {img_id} → {dur}s")
            else:
                print(f"  场景 {i+1}/{len(scenes)}: ❌ {img_id} 未找到，跳过")
                continue
            total_dur += dur

        if not scene_files:
            print(f"❌ {dir_name}: 没有可用场景")
            return None

        print(f"🎬 生成视频片段...")
        clip_files = []
        for i, (img_file, dur) in enumerate(scene_files):
            clip_file = tmp / f"clip_{i:02d}.mp4"
            cmd = [
                str(FFMPEG), "-y",
                "-loop", "1", "-i", img_file,
                "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},fps={FPS}",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-t", str(dur),
                str(clip_file)
            ]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0:
                clip_files.append(str(clip_file))
                print(f"  片段 {i+1}/{len(scene_files)} ✅")
            else:
                print(f"  片段 {i+1} ❌: {r.stderr[-200:]}")
        if not clip_files:
            return None

        concat_list = tmp / "concat.txt"
        with open(concat_list, "w") as f:
            for cf in clip_files:
                f.write(f"file '{cf}'\n")

        video_only = tmp / "video_only.mp4"
        cmd = [
            str(FFMPEG), "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-pix_fmt", "yuv420p",
            str(video_only)
        ]
        print(f"✂️  拼接...")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"❌ 拼接失败: {r.stderr[-300:]}")
            return None

        output_file = proj_dir / f"output_{dir_name}.mp4"
        cmd = [
            str(FFMPEG), "-y",
            "-i", str(video_only),
            "-i", music_file,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(output_file)
        ]
        print(f"🎵 添加音频...")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"❌ 音频失败: {r.stderr[-200:]}")
            return None

        size_mb = os.path.getsize(output_file) / 1024 / 1024
        print(f"✅ 完成: {output_file} ({total_dur}s={total_dur/60:.1f}min, {size_mb:.1f}MB)")
        return output_file

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 批量组装视频 #02-#10")
    print("=" * 60)
    
    results = {}
    for dir_name, scenes in ALL_VIDEOS:
        print(f"\n{'='*50}")
        print(f"🎬 生成: {dir_name}")
        print(f"{'='*50}")
        result = assemble_video(dir_name, scenes)
        results[dir_name] = result
    
    print("\n\n" + "=" * 60)
    print("📊 批量生成完成 - 汇总")
    print("=" * 60)
    for dir_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {dir_name}")
        if result:
            size_mb = os.path.getsize(result) / 1024 / 1024
            print(f"      {result} ({size_mb:.1f}MB)")
    
    # Copy to Windows Desktop
    DESKTOP_WIN = Path("/mnt/c/Users/admin/Desktop")
    for dir_name, result in results.items():
        if result and DESKTOP_WIN.exists():
            dest = DESKTOP_WIN / f"output_{dir_name}.mp4"
            shutil.copy2(result, dest)
            print(f"📁 复制到桌面: {dest}")
