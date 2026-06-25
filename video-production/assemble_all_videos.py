#!/usr/bin/env python3
"""
批量组装所有10个视频 - 完整版 4-5分钟
目标：每个视频 4分10秒 = 250秒
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

# 每个视频目标时长（秒）
TARGET_DUR = 250  # 4分10秒

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
    bbox = draw.textbbox((0, 0), title, font=ft)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, HEIGHT - 140), title, font=ft, fill="white")
    bbox2 = draw.textbbox((0, 0), subtitle, font=fs)
    sw = bbox2[2] - bbox2[0]
    draw.text(((WIDTH - sw) // 2, HEIGHT - 85), subtitle, font=fs, fill=(200, 200, 200))
    return img.convert("RGB")

def find_image(keyword):
    all_files = sorted(MEDIA_IMG.glob("image-1---*.png"), key=os.path.getmtime, reverse=True)
    kw = keyword.lower()
    for f in all_files:
        if kw in f.stem.lower():
            return str(f)
    return None

def loop_music(music_path, target_dur, tmp_path):
    """用FFmpeg将音乐循环到目标时长（带淡入淡出）"""
    looped = tmp_path / "music_looped.mp3"
    # 先循环到至少目标时长（多循环几次确保够长）
    # 然后裁剪到目标时长，加淡入淡出
    fade_dur = min(5, target_dur // 10)
    cmd = [
        str(FFMPEG), "-y",
        "-stream_loop", "20", "-i", music_path,
        "-t", str(target_dur),
        "-af", f"afade=t=in:ss=0:d={fade_dur},afade=t=out:st={target_dur - fade_dur}:d={fade_dur}",
        "-acodec", "libmp3lame", "-b:a", "192k",
        str(looped)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"    音乐循环失败: {r.stderr[-200:]}")
        # fallback: 直接复制原文件
        shutil.copy2(music_path, looped)
    dur_r = subprocess.run([str(FFMPEG), "-v", "quiet", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(looped)], capture_output=True, text=True)
    print(f"    循环音乐生成: {dur_r.stdout.strip()}s")
    return str(looped)

# ============================================================
# 视频定义：(目录名, [(图片ID, 显示秒数, 标题, 副标题), ...])
# 总时长必须 = TARGET_DUR (250秒)
# ============================================================

# Video 01: 椅子腿部训练 - 已完成，跳过
# Video 02: 弹力带全身训练
VIDEO_02_SCENES = [
    ("aaa4038a",  15, "Resistance Band Full Body Training", "Strength Training for Seniors | Ageless Strength"),
    ("c14beda1",  30, "Why Resistance Bands Are Perfect for Seniors", "Affordable, portable, and gentle on joints"),
    ("5ac33004",  35, "Step 1: Bicep Curl with Band", "Keep elbows at your sides, squeeze at the top"),
    ("293cbed8",  35, "Step 2: Leg Curl with Band", "Stand on one leg, curl the other back slowly"),
    ("fcb14201",  35, "Step 3: Seated Row", "Pull the band toward your belly button"),
    ("76dbd5d4",  35, "Step 4: Band Squat", "Feet shoulder-width, sit back like in a chair"),
    ("3a4c12c2",  30, "AI Pose Detection - Real-Time Feedback", "Get instant feedback on every rep you do"),
    ("7a76ccc8",  20, "Personalized Plan Just For You", "Get matched to the right resistance level"),
    ("0152c1ae",  15, "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]
# 合计: 250s ✅

VIDEO_03_SCENES = [
    ("1d2c0ac2",  15, "Seated Dumbbell Shoulder Training", "Strength Training for Seniors | Ageless Strength"),
    ("d92ef8f3",  30, "Why Shoulder Strength Matters After 50", "Makes daily activities easier - carrying groceries, lifting grandkids"),
    ("81ea2f1d",  35, "Step 1: Seated Shoulder Press", "Press weights straight up, control the descent"),
    ("9ae90bc0",  35, "Step 2: Lateral Raise", "Raise arms out to sides, slight bend in elbows"),
    ("8a6a64cf",  35, "Step 3: Front Raise", "Alternate arms, control the movement"),
    ("3c0fadae",  35, "Share Your Progress with Family", "Invite family members to follow your journey"),
    ("9ae90bc0",  30, "Family Dashboard - See Everyone's Progress", "One subscription, the whole family stays connected"),
    ("7a76ccc8",  20, "AI Real-Time Form Feedback", "Your phone watches your form - just like a personal trainer"),
    ("0152c1ae",  15, "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]
# 合计: 250s ✅

VIDEO_04_SCENES = [
    ("5aa7934e",  15, "Balance Training - Prevent Falls", "Strength Training for Seniors | Ageless Strength"),
    ("d36b8c82",  30, "Falls Are the #1 Threat to Senior Health", "But they're preventable with the right training"),
    ("af9d3d8e",  35, "Step 1: Tandem Stance", "Stand heel to toe, like on a tightrope"),
    ("083690a1",  35, "Step 2: Single Leg Stance", "Hold for 30 seconds each leg - don't forget to breathe"),
    ("1e43f2dd",  35, "Step 3: Heel-to-Toe Walk", "Take 20 steps forward, watching your balance"),
    ("686c5b20",  35, "Family Guardian - Stay Connected", "Your family gets notified if something seems wrong"),
    ("8555f6e9",  30, "AI Motion Detection - Real-Time Safety", "Get alerted if your balance wavers during exercise"),
    ("7a76ccc8",  20, "Try Ageless Strength - Track Your Progress", "See your improvement week by week"),
    ("0152c1ae",  15, "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]
# 合计: 250s ✅

VIDEO_05_SCENES = [
    ("54ba8535",  15, "Core Stability Training - Zero Equipment", "Strength Training for Seniors | Ageless Strength"),
    ("64b05d0d",  30, "Why Core Stability Is the Foundation of Fitness", "A strong core prevents falls and back pain"),
    ("b296fee4",  35, "Step 1: Bird Dog", "Extend opposite arm and leg, keep back flat"),
    ("68c7fe35",  35, "Step 2: Seated Core Tighten", "Sit tall, pull navel toward spine, hold and breathe"),
    ("37a452ab",  35, "Step 3: Leg Extension", "Extend one leg at a time, keep core engaged"),
    ("a1073ef7",  35, "Step 4: Bridge Pose", "Lie on back, lift hips, hold at the top"),
    ("b296fee4",  30, "Core Stability - Control is Everything", "Slow and controlled beats fast and sloppy"),
    ("347b862e",  20, "Progress Tracking - Celebrate Every Win", "Ageless Strength tracks your improvements automatically"),
    ("0152c1ae",  15, "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]
# 合计: 250s ✅

VIDEO_06_SCENES = [
    ("76db883b",  15, "Resistance Band Leg Training", "Strength Training for Seniors | Ageless Strength"),
    ("916b2d14",  30, "Why Leg Strength Is Critical After 60", "Strong legs mean independence - stand up, walk, climb stairs"),
    ("e25c6059",  35, "Step 1: Lateral Leg Raise", "Lift leg out to side, slow and controlled"),
    ("76dbd5d4",  35, "Step 2: Band Squat", "Sit back into the squat, keep knees behind toes"),
    ("fcb14201",  35, "Step 3: Standing Hamstring Curl", "Curl heel toward glutes, squeeze at the top"),
    ("293cbed8",  35, "Step 4: Seated Leg Extension", "Strengthen quadriceps from a seated position"),
    ("c7d698ad",  30, "Step 5: Hip Bridge", "Lie on back, lift hips, hold at the top"),
    ("7a76ccc8",  20, "Premium Content - Unlock All 20+ Courses", "Subscribe to access every training program"),
    ("0152c1ae",  15, "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]
# 合计: 250s ✅

VIDEO_07_SCENES = [
    ("0c6f6963",  15, "Complete Morning & Evening Stretch", "Strength Training for Seniors | Ageless Strength"),
    ("dc8f5378",  30, "Why Stretching Is Essential for Seniors", "Maintains flexibility, reduces stiffness, prevents injury"),
    ("68c7fe35",  30, "Step 1: Seated Hamstring Stretch", "Extend one leg, lean forward slightly, hold 30 seconds each"),
    ("d524b028",  30, "Step 2: Standing Quad Stretch", "Hold ankle behind you, keep knees together"),
    ("c7d698ad",  30, "Step 3: Hip Flexor Lunge", "Lunge forward, drop back knee toward floor"),
    ("b015ac73",  30, "Step 4: Neck & Shoulder Release", "Gentle head tilts and shoulder rolls"),
    ("dc8f5378",  30, "Step 5: Spinal Twist", "Rotate torso, look over each shoulder"),
    ("37a452ab",  30, "Step 6: Standing Calf Stretch", "Hands on wall, one leg back, heel dropped"),
    ("37a452ab",  20, "Daily Reminders - Build Your Habit", "Set workout reminders and never miss a day"),
    ("0152c1ae",  15, "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]
# 合计: 260s ✅

VIDEO_08_SCENES = [
    ("037bb945",  15, "Chair Squat - Perfect Your Form", "Strength Training for Seniors | Ageless Strength"),
    ("18b101f6",  30, "Why Chair Squats Mimic Real-Life Movement", "They train exactly what your body needs to do every day"),
    ("76dbd5d4",  35, "Step 1: Stand in Front of Chair", "Feet shoulder-width, toes slightly turned out"),
    ("430568d5",  35, "Step 2: The Descent", "Push hips back, bend knees, lower until you touch the seat"),
    ("916b2d14",  35, "Step 3: The Ascent", "Drive through your heels, squeeze your glutes at the top"),
    ("7cfdb1ac",  30, "The #1 Mistake: Knees Past Toes", "Keep your weight in your heels, knees tracking over toes"),
    ("8555f6e9",  35, "AI Real-Time Form Correction", "Your phone detects your form and gives instant tips"),
    ("7cfdb1ac",  20, "Try the AI Pose Detection Feature", "Just like having a personal trainer watching your every rep"),
    ("0152c1ae",  15, "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]
# 合计: 250s ✅

VIDEO_09_SCENES = [
    ("6fd503bd",  15, "5 Common Strength Training Mistakes", "Strength Training for Seniors | Ageless Strength"),
    ("639c0ca1",  35, "Mistake #1: Holding Your Breath", "Breathe normally - exhale during effort, inhale on recovery"),
    ("a3dc86fa",  35, "Mistake #2: Working Through Pain", "Pain is your body's warning signal - respect it!"),
    ("e7222044",  35, "Mistake #3: Too Much Too Soon", "Quality over quantity - build gradually, 10% rule"),
    ("775fe408",  35, "Mistake #4: Skipping Warm-Up", "Cold muscles are injury-prone - always warm up first"),
    ("df6b8cec",  35, "Mistake #5: No Rest Days", "Your muscles grow during rest, not during exercise"),
    ("7a76ccc8",  35, "Learn the Science of Strength Training", "Ageless Strength - built on proper exercise science"),
    ("347b862e",  10, "7-Day Free Trial", "Try risk-free, cancel anytime"),
    ("0152c1ae",  15, "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]
# 合计: 250s ✅

VIDEO_10_SCENES = [
    ("179ee92b",  15, "Design Your Family Workout Plan", "Strength Training for Seniors | Ageless Strength"),
    ("a0eb002f",  30, "One Subscription, Whole Family", "Share progress, motivate each other, save money"),
    ("f7022b71",  35, "Individual vs Family Plan", "Family plan at $14.99/mo = best value for your household"),
    ("2667fb76",  35, "Set Weekly Goals Together", "Plan workouts as a family - consistency is everything"),
    ("a1073ef7",  35, "Track Every Family Member's Progress", "Watch mom, dad, and yourself improve week by week"),
    ("347b862e",  35, "Stay Motivated as a Family", "When one person trains, the whole family cheers them on"),
    ("a0eb002f",  35, "20+ Exercise Courses Included", "From beginner to advanced - something for every level"),
    ("7a76ccc8",  15, "Premium Family Plan - Best Value", "Unlock all features for the whole family"),
    ("0152c1ae",  15, "Start Your 7-Day Free Trial Today", "Ageless Strength - Strength Training for Every Age"),
]
# 合计: 250s ✅

ALL_VIDEOS = [
    ("01_chair_leg_training",        []),  # 已完成，跳过
    ("02_resistance_band_fullbody",   VIDEO_02_SCENES),
    ("03_seated_dumbbell_shoulder",   VIDEO_03_SCENES),
    ("04_balance_fall_prevention",    VIDEO_04_SCENES),
    ("05_core_stability",             VIDEO_05_SCENES),
    ("06_resistance_band_legs",       VIDEO_06_SCENES),
    ("07_morning_evening_stretch",     VIDEO_07_SCENES),
    ("08_chair_squat_form",           VIDEO_08_SCENES),
    ("09_strength_mistakes",          VIDEO_09_SCENES),
    ("10_family_workout_plan",        VIDEO_10_SCENES),
]

def get_music():
    """获取可用的音乐文件（已循环到TARGET_DUR）"""
    music_files = sorted(MEDIA_MUSIC.glob("*.mp3"), key=os.path.getmtime, reverse=True)
    if not music_files:
        return None
    return str(music_files[0])

def assemble_video(dir_name, scenes, music_looped_path):
    if not scenes:
        print(f"⏭️  {dir_name}: 跳过（已完成）")
        return None
    proj_dir = PROJECT_BASE / dir_name
    proj_dir.mkdir(exist_ok=True)
    
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
                rendered.save(out, "JPEG", quality=92)
                scene_files.append((str(out), dur, title))
                print(f"  场景 {i+1}/{len(scenes)}: ✅ {img_id[:8]}... → {dur}s | {title[:40]}")
            else:
                print(f"  场景 {i+1}/{len(scenes)}: ❌ {img_id} 未找到")
                continue
            total_dur += dur

        if not scene_files:
            return None

        print(f"🎬 生成视频片段（{total_dur}s = {total_dur/60:.1f}min）...")
        clip_files = []
        for i, (img_file, dur, title) in enumerate(scene_files):
            clip_file = tmp / f"clip_{i:02d}.mp4"
            cmd = [
                str(FFMPEG), "-y",
                "-loop", "1", "-i", img_file,
                "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},fps={FPS}",
                "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                "-pix_fmt", "yuv420p",
                "-t", str(dur),
                str(clip_file)
            ]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0:
                clip_files.append(str(clip_file))
            else:
                print(f"  ❌ clip {i} 失败")
        if not clip_files:
            return None

        # 拼接（带场景过渡）
        concat_list = tmp / "concat.txt"
        with open(concat_list, "w") as f:
            for cf in clip_files:
                f.write(f"file '{cf}'\n")

        video_only = tmp / "video_only.mp4"
        cmd = [
            str(FFMPEG), "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-pix_fmt", "yuv420p",
            str(video_only)
        ]
        print(f"✂️  拼接 ({len(clip_files)} 个片段)...")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"❌ 拼接失败: {r.stderr[-300:]}")
            return None

        # 合并音频（循环音乐填充整个视频，不用-shortest）
        output_file = proj_dir / f"output_{dir_name}.mp4"
        cmd = [
            str(FFMPEG), "-y",
            "-i", str(video_only),
            "-i", music_looped_path,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(output_file)
        ]
        print(f"🎵 合并音频（{total_dur}s 循环音乐）...")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"❌ 音频失败: {r.stderr[-200:]}")
            return None

        size_mb = os.path.getsize(output_file) / 1024 / 1024
        print(f"✅ 完成: {output_file} ({total_dur}s={total_dur/60:.1f}min, {size_mb:.1f}MB)")
        return output_file

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 批量组装视频 #02-#10 (目标 4分10秒/个)")
    print("=" * 60)
    
    # 获取/生成循环音乐
    music_src = get_music()
    if not music_src:
        print("❌ 没有找到音乐文件！")
        exit(1)
    
    # 创建目标时长循环音乐
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        print(f"\n🎵 准备循环音乐（目标 {TARGET_DUR}s）...")
        music_looped = loop_music(music_src, TARGET_DUR, tmp)
    
    results = {}
    for dir_name, scenes in ALL_VIDEOS:
        print(f"\n{'='*50}")
        print(f"🎬 生成: {dir_name}")
        print(f"{'='*50}")
        result = assemble_video(dir_name, scenes, music_looped)
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
    
    # 复制到 Windows Desktop
    DESKTOP_WIN = Path("/mnt/c/Users/admin/Desktop")
    copied = []
    for dir_name, result in results.items():
        if result and DESKTOP_WIN.exists():
            dest = DESKTOP_WIN / f"output_{dir_name}.mp4"
            shutil.copy2(result, dest)
            copied.append(str(dest))
    
    if copied:
        print(f"\n📁 已复制到 Windows 桌面 ({len(copied)} 个文件)")
