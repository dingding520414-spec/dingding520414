#!/usr/bin/env python3
"""批量组装视频 v2 - 使用预生成的250秒循环音乐"""
import imageio_ffmpeg, subprocess, os, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import tempfile

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
WIDTH, HEIGHT = 1280, 720
FPS = 25
MEDIA_IMG = Path("/home/admin1234/.openclaw/media/tool-image-generation")
PROJECT_BASE = Path("/home/admin1234/.openclaw/workspace/projects/senior-strength-app/video-production")
LOOPED_MUSIC = "/tmp/music_looped_250s.mp3"  # 预生成
TARGET_DUR = 250

def get_font(size=36):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def resize_crop(img_path):
    img = Image.open(img_path).convert("RGB")
    scale = max(WIDTH / img.width, HEIGHT / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    l, t = (nw - WIDTH) // 2, (nh - HEIGHT) // 2
    return img.crop((l, t, l + WIDTH, t + HEIGHT))

def render_scene(img_path, title, subtitle):
    img = resize_crop(img_path)
    ov = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    draw = ImageDraw.Draw(ov)
    for y in range(HEIGHT - 180, HEIGHT):
        alpha = int(210 * (y - (HEIGHT - 180)) / 180)
        draw.rectangle([(0,y),(WIDTH,y+1)], fill=(0,0,0,alpha))
    img = Image.alpha_composite(img.convert("RGBA"), ov)
    draw = ImageDraw.Draw(img)
    ft, fs = get_font(42), get_font(26)
    for txt, font, y, color in [(title, ft, HEIGHT-140, "white"), (subtitle, fs, HEIGHT-85, (200,200,200))]:
        b = draw.textbbox((0,0), txt, font=font)
        w = b[2]-b[0]
        draw.text(((WIDTH-w)//2, y), txt, font=font, fill=color)
    return img.convert("RGB")

def find_image(kw):
    files = sorted(MEDIA_IMG.glob("image-1---*.png"), key=os.path.getmtime, reverse=True)
    kw = kw.lower()
    for f in files:
        if kw in f.stem.lower(): return str(f)
    return None

SCENES = {
    "02_resistance_band_fullbody": [
        ("aaa4038a", 15, "Resistance Band Full Body Training","Strength Training for Seniors | Ageless Strength"),
        ("c14beda1", 30, "Why Resistance Bands Are Perfect for Seniors","Affordable, portable, and gentle on joints"),
        ("5ac33004", 35, "Step 1: Bicep Curl with Band","Keep elbows at your sides, squeeze at the top"),
        ("293cbed8", 35, "Step 2: Leg Curl with Band","Stand on one leg, curl the other back slowly"),
        ("fcb14201", 35, "Step 3: Seated Row","Pull the band toward your belly button"),
        ("76dbd5d4", 35, "Step 4: Band Squat","Feet shoulder-width, sit back like in a chair"),
        ("3a4c12c2", 30, "AI Pose Detection - Real-Time Feedback","Get instant feedback on every rep you do"),
        ("7a76ccc8", 20, "Personalized Plan Just For You","Get matched to the right resistance level"),
        ("0152c1ae", 15, "Start Your 7-Day Free Trial Today","Ageless Strength - Strength Training for Every Age"),
    ],
    "03_seated_dumbbell_shoulder": [
        ("1d2c0ac2", 15, "Seated Dumbbell Shoulder Training","Strength Training for Seniors | Ageless Strength"),
        ("d92ef8f3", 30, "Why Shoulder Strength Matters After 50","Makes daily activities easier - carrying groceries, lifting grandkids"),
        ("81ea2f1d", 35, "Step 1: Seated Shoulder Press","Press weights straight up, control the descent"),
        ("9ae90bc0", 35, "Step 2: Lateral Raise","Raise arms out to sides, slight bend in elbows"),
        ("8a6a64cf", 35, "Step 3: Front Raise","Alternate arms, control the movement"),
        ("3c0fadae", 35, "Share Your Progress with Family","Invite family members to follow your journey"),
        ("9ae90bc0", 30, "Family Dashboard - See Everyone's Progress","One subscription, the whole family stays connected"),
        ("7a76ccc8", 20, "AI Real-Time Form Feedback","Your phone watches your form - like a personal trainer"),
        ("0152c1ae", 15, "Start Your 7-Day Free Trial Today","Ageless Strength - Strength Training for Every Age"),
    ],
    "04_balance_fall_prevention": [
        ("5aa7934e", 15, "Balance Training - Prevent Falls","Strength Training for Seniors | Ageless Strength"),
        ("d36b8c82", 30, "Falls Are the #1 Threat to Senior Health","But they're preventable with the right training"),
        ("af9d3d8e", 35, "Step 1: Tandem Stance","Stand heel to toe, like on a tightrope"),
        ("083690a1", 35, "Step 2: Single Leg Stance","Hold for 30 seconds each leg - don't forget to breathe"),
        ("1e43f2dd", 35, "Step 3: Heel-to-Toe Walk","Take 20 steps forward, watching your balance"),
        ("686c5b20", 35, "Family Guardian - Stay Connected","Your family gets notified if something seems wrong"),
        ("8555f6e9", 30, "AI Motion Detection - Real-Time Safety","Get alerted if your balance wavers during exercise"),
        ("7a76ccc8", 20, "Try Ageless Strength - Track Your Progress","See your improvement week by week"),
        ("0152c1ae", 15, "Start Your 7-Day Free Trial Today","Ageless Strength - Strength Training for Every Age"),
    ],
    "05_core_stability": [
        ("54ba8535", 15, "Core Stability Training - Zero Equipment","Strength Training for Seniors | Ageless Strength"),
        ("64b05d0d", 30, "Why Core Stability Is the Foundation","A strong core prevents falls and back pain"),
        ("b296fee4", 35, "Step 1: Bird Dog","Extend opposite arm and leg, keep back flat"),
        ("68c7fe35", 35, "Step 2: Seated Core Tighten","Sit tall, pull navel toward spine, hold and breathe"),
        ("37a452ab", 35, "Step 3: Leg Extension","Extend one leg at a time, keep core engaged"),
        ("a1073ef7", 35, "Step 4: Bridge Pose","Lie on back, lift hips, hold at the top"),
        ("b296fee4", 30, "Core Stability - Control is Everything","Slow and controlled beats fast and sloppy"),
        ("347b862e", 20, "Progress Tracking - Celebrate Every Win","Ageless Strength tracks your improvements automatically"),
        ("0152c1ae", 15, "Start Your 7-Day Free Trial Today","Ageless Strength - Strength Training for Every Age"),
    ],
    "06_resistance_band_legs": [
        ("76db883b", 15, "Resistance Band Leg Training","Strength Training for Seniors | Ageless Strength"),
        ("916b2d14", 30, "Why Leg Strength Is Critical After 60","Strong legs mean independence - stand up, walk, climb stairs"),
        ("e25c6059", 35, "Step 1: Lateral Leg Raise","Lift leg out to side, slow and controlled"),
        ("76dbd5d4", 35, "Step 2: Band Squat","Sit back into the squat, keep knees behind toes"),
        ("fcb14201", 35, "Step 3: Standing Hamstring Curl","Curl heel toward glutes, squeeze at the top"),
        ("293cbed8", 35, "Step 4: Seated Leg Extension","Strengthen quadriceps from a seated position"),
        ("c7d698ad", 30, "Step 5: Hip Bridge","Lie on back, lift hips, hold at the top"),
        ("7a76ccc8", 20, "Premium Content - Unlock All 20+ Courses","Subscribe to access every training program"),
        ("0152c1ae", 15, "Start Your 7-Day Free Trial Today","Ageless Strength - Strength Training for Every Age"),
    ],
    "07_morning_evening_stretch": [
        ("0c6f6963", 15, "Complete Morning & Evening Stretch","Strength Training for Seniors | Ageless Strength"),
        ("dc8f5378", 30, "Why Stretching Is Essential for Seniors","Maintains flexibility, reduces stiffness, prevents injury"),
        ("68c7fe35", 30, "Step 1: Seated Hamstring Stretch","Extend one leg, lean forward slightly, hold 30 seconds each"),
        ("d524b028", 30, "Step 2: Standing Quad Stretch","Hold ankle behind you, keep knees together"),
        ("c7d698ad", 30, "Step 3: Hip Flexor Lunge","Lunge forward, drop back knee toward floor"),
        ("b015ac73", 30, "Step 4: Neck & Shoulder Release","Gentle head tilts and shoulder rolls"),
        ("dc8f5378", 30, "Step 5: Spinal Twist","Rotate torso, look over each shoulder"),
        ("37a452ab", 30, "Step 6: Standing Calf Stretch","Hands on wall, one leg back, heel dropped"),
        ("37a452ab", 20, "Daily Reminders - Build Your Habit","Set workout reminders and never miss a day"),
        ("0152c1ae", 15, "Start Your 7-Day Free Trial Today","Ageless Strength - Strength Training for Every Age"),
    ],
    "08_chair_squat_form": [
        ("037bb945", 15, "Chair Squat - Perfect Your Form","Strength Training for Seniors | Ageless Strength"),
        ("18b101f6", 30, "Why Chair Squats Mimic Real-Life Movement","They train exactly what your body needs to do every day"),
        ("76dbd5d4", 35, "Step 1: Stand in Front of Chair","Feet shoulder-width, toes slightly turned out"),
        ("430568d5", 35, "Step 2: The Descent","Push hips back, bend knees, lower until you touch the seat"),
        ("916b2d14", 35, "Step 3: The Ascent","Drive through your heels, squeeze your glutes at the top"),
        ("7cfdb1ac", 30, "The #1 Mistake: Knees Past Toes","Keep your weight in your heels, knees tracking over toes"),
        ("8555f6e9", 35, "AI Real-Time Form Correction","Your phone detects your form and gives instant tips"),
        ("7cfdb1ac", 20, "Try the AI Pose Detection Feature","Just like having a personal trainer watching your every rep"),
        ("0152c1ae", 15, "Start Your 7-Day Free Trial Today","Ageless Strength - Strength Training for Every Age"),
    ],
    "09_strength_mistakes": [
        ("6fd503bd", 15, "5 Common Strength Training Mistakes","Strength Training for Seniors | Ageless Strength"),
        ("639c0ca1", 35, "Mistake #1: Holding Your Breath","Breathe normally - exhale during effort, inhale on recovery"),
        ("a3dc86fa", 35, "Mistake #2: Working Through Pain","Pain is your body's warning signal - respect it!"),
        ("e7222044", 35, "Mistake #3: Too Much Too Soon","Quality over quantity - build gradually, 10% rule"),
        ("775fe408", 35, "Mistake #4: Skipping Warm-Up","Cold muscles are injury-prone - always warm up first"),
        ("df6b8cec", 35, "Mistake #5: No Rest Days","Your muscles grow during rest, not during exercise"),
        ("7a76ccc8", 35, "Learn the Science of Strength Training","Ageless Strength - built on proper exercise science"),
        ("347b862e", 10, "7-Day Free Trial","Try risk-free, cancel anytime"),
        ("0152c1ae", 15, "Start Your 7-Day Free Trial Today","Ageless Strength - Strength Training for Every Age"),
    ],
    "10_family_workout_plan": [
        ("179ee92b", 15, "Design Your Family Workout Plan","Strength Training for Seniors | Ageless Strength"),
        ("a0eb002f", 30, "One Subscription, Whole Family","Share progress, motivate each other, save money"),
        ("f7022b71", 35, "Individual vs Family Plan","Family plan at $14.99/mo = best value for your household"),
        ("2667fb76", 35, "Set Weekly Goals Together","Plan workouts as a family - consistency is everything"),
        ("a1073ef7", 35, "Track Every Family Member's Progress","Watch mom, dad, and yourself improve week by week"),
        ("347b862e", 35, "Stay Motivated as a Family","When one person trains, the whole family cheers them on"),
        ("a0eb002f", 35, "20+ Exercise Courses Included","From beginner to advanced - something for every level"),
        ("7a76ccc8", 15, "Premium Family Plan - Best Value","Unlock all features for the whole family"),
        ("0152c1ae", 15, "Start Your 7-Day Free Trial Today","Ageless Strength - Strength Training for Every Age"),
    ],
}

def make_video(dir_name, scenes):
    proj_dir = PROJECT_BASE / dir_name
    proj_dir.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # 渲染场景
        frames = []
        total = 0
        for i, (kw, dur, title, sub) in enumerate(scenes):
            path = find_image(kw)
            if not path:
                print(f"  ❌ [{i+1}] {kw} 未找到"); continue
            img = render_scene(path, title, sub)
            out = tmp / f"f_{i:02d}.jpg"
            img.save(out, "JPEG", quality=92)
            frames.append((str(out), dur))
            total += dur

        # 生成片段
        clips = []
        for i, (fp, dur) in enumerate(frames):
            cp = tmp / f"c_{i:02d}.mp4"
            r = subprocess.run([str(FFMPEG), "-y", "-loop","1","-i",fp,
                "-vf",f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},fps={FPS}",
                "-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p",
                "-t",str(dur), str(cp)], capture_output=True, text=True)
            if r.returncode == 0:
                clips.append(str(cp))
                print(f"  ✅ clip {i+1}/{len(frames)} ({dur}s)")
            else:
                print(f"  ❌ clip {i+1} 失败")

        if not clips: return None
        # 拼接
        cat = tmp/"list.txt"
        with open(cat,"w") as f:
            for c in clips: f.write(f"file '{c}'\n")
        video_out = tmp/"v.mp4"
        r = subprocess.run([str(FFMPEG), "-y", "-f","concat","-safe","0","-i",str(cat),
            "-c:v","libx264","-preset","fast","-crf","22","-pix_fmt","yuv420p", str(video_out)],
            capture_output=True, text=True)
        if r.returncode != 0: print(f"❌ 拼接: {r.stderr[-200:]}"); return None

        out = proj_dir / f"output_{dir_name}.mp4"
        r = subprocess.run([str(FFMPEG), "-y", "-i", str(video_out), "-i", LOOPED_MUSIC,
            "-c:v","copy", "-c:a","aac","-b:a","192k", "-shortest", str(out)],
            capture_output=True, text=True)
        if r.returncode != 0: print(f"❌ 音频: {r.stderr[-200:]}"); return None
        sz = os.path.getsize(out)/1024/1024
        print(f"  → {out} ({total}s={total/60:.1f}min, {sz:.1f}MB)")
        return out

if __name__ == "__main__":
    print(f"🎬 批量生成9个视频（每个{TARGET_DUR}s={TARGET_DUR/60:.1f}min）")
    print(f"🎵 音乐: {LOOPED_MUSIC}")
    results = {}
    for name, scenes in SCENES.items():
        print(f"\n▶ {name}")
        r = make_video(name, scenes)
        results[name] = r

    DESKTOP = Path("/mnt/c/Users/admin/Desktop")
    ok = [n for n,r in results.items() if r]
    print(f"\n✅ 完成 {len(ok)}/9 个视频")
    for n,r in results.items():
        status = "✅" if r else "❌"
        print(f"  {status} {n}")
        if r and DESKTOP.exists():
            d = DESKTOP/f"output_{n}.mp4"
            shutil.copy2(r, d)
            print(f"     → {d}")
