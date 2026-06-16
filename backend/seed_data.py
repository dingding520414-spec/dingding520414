"""
Seed data script for initial courses.
Run with: python seed_data.py
"""
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.models.models import Course, Exercise, Base
from app.core.config import get_settings

settings = get_settings()

COURSES_DATA = [
    {
        "title": "椅子深蹲入门",
        "description": "专为老年人设计的入门级深蹲训练，利用椅子作为支撑，确保安全。动作简单易学，适合力量训练初学者。",
        "difficulty": 1,
        "duration_min": 10,
        "exercises": [
            {"name": "热身 - 关节活动", "description": "缓慢转动手腕、脚踝、膝盖和髋关节", "reps": 10, "duration_sec": 120, "order_index": 1},
            {"name": "扶椅站立", "description": "双手扶椅，缓慢坐下再站起，保持平衡", "reps": 8, "duration_sec": 120, "order_index": 2},
            {"name": "半深蹲", "description": "扶椅，下蹲至膝盖弯曲约45度，膝盖不超过脚尖", "reps": 8, "duration_sec": 120, "order_index": 3},
            {"name": "踮脚站立", "description": "扶椅，踮起脚尖保持3秒，慢慢放下", "reps": 10, "duration_sec": 90, "order_index": 4},
            {"name": "侧身抬腿", "description": "扶椅，侧抬右腿保持3秒，换腿", "reps": 8, "duration_sec": 120, "order_index": 5},
            {"name": "放松拉伸", "description": "站立深呼吸，手臂上举放松", "reps": 5, "duration_sec": 60, "order_index": 6},
        ]
    },
    {
        "title": "墙壁俯卧撑",
        "description": "利用墙壁进行俯卧撑训练，强度适中，适合老年人增强上肢力量。",
        "difficulty": 1,
        "duration_min": 10,
        "exercises": [
            {"name": "热身 - 肩部活动", "description": "双手扶墙，画圈活动肩关节", "reps": 10, "duration_sec": 60, "order_index": 1},
            {"name": "墙壁俯卧撑", "description": "双手撑墙，身体倾斜15度，弯曲手肘做俯卧撑", "reps": 10, "duration_sec": 120, "order_index": 2},
            {"name": "墙壁侧推", "description": "右手撑墙，左手推墙，身体转向右侧", "reps": 10, "duration_sec": 90, "order_index": 3},
            {"name": "墙壁夹背", "description": "双手撑墙，手肘夹紧身体，锻炼背部", "reps": 10, "duration_sec": 90, "order_index": 4},
            {"name": "放松", "description": "深呼吸，双臂自然下垂", "reps": 5, "duration_sec": 60, "order_index": 5},
        ]
    },
    {
        "title": "弹力带手臂训练",
        "description": "使用弹力带进行上肢力量训练，增强手臂和肩部肌肉，改善日常活动能力。",
        "difficulty": 2,
        "duration_min": 12,
        "exercises": [
            {"name": "热身", "description": "空手挥臂热身", "reps": 10, "duration_sec": 60, "order_index": 1},
            {"name": "弹力带二头弯举", "description": "双脚踩弹力带，双手弯举锻炼二头肌", "reps": 12, "duration_sec": 120, "order_index": 2},
            {"name": "弹力带肩推", "description": "弹力带放在身后，双手向上推举", "reps": 10, "duration_sec": 120, "order_index": 3},
            {"name": "弹力带划船", "description": "弹力带固定前方，双手向后拉伸", "reps": 12, "duration_sec": 120, "order_index": 4},
            {"name": "弹力带臂伸展", "description": "弹力带固定身后，单手向后伸直", "reps": 10, "duration_sec": 120, "order_index": 5},
            {"name": "弹力带胸前推", "description": "弹力带置于胸前，双手向前推出", "reps": 12, "duration_sec": 90, "order_index": 6},
            {"name": "弹力带侧平举", "description": "弹力带踩在脚下，双手侧平举", "reps": 10, "duration_sec": 90, "order_index": 7},
            {"name": "放松拉伸", "description": "肩部拉伸放松", "reps": 5, "duration_sec": 60, "order_index": 8},
        ]
    },
    {
        "title": "弹力带腿部训练",
        "description": "专门针对下肢的力量训练，增强腿部肌肉，预防跌倒。",
        "difficulty": 2,
        "duration_min": 12,
        "exercises": [
            {"name": "热身", "description": "原地踏步热身", "reps": 20, "duration_sec": 60, "order_index": 1},
            {"name": "弹力带深蹲", "description": "弹力带绕大腿，屈髋屈膝下蹲", "reps": 10, "duration_sec": 120, "order_index": 2},
            {"name": "弹力带腿弯举", "description": "站立，弹力带绕脚踝向后弯举", "reps": 12, "duration_sec": 90, "order_index": 3},
            {"name": "弹力带腿伸展", "description": "坐姿，弹力带绕脚踝向前伸直", "reps": 12, "duration_sec": 90, "order_index": 4},
            {"name": "弹力带侧向行走", "description": "弹力带绕膝，慢速横向行走", "reps": 20, "duration_sec": 120, "order_index": 5},
            {"name": "弹力带站立提踵", "description": "弹力带踩脚下，踮脚尖站立", "reps": 15, "duration_sec": 90, "order_index": 6},
            {"name": "弹力带坐姿腿内收", "description": "坐姿，弹力带绕膝盖内侧抗阻内收", "reps": 12, "duration_sec": 90, "order_index": 7},
            {"name": "弹力带坐姿腿外展", "description": "坐姿，弹力带绕膝盖外侧抗阻外展", "reps": 12, "duration_sec": 90, "order_index": 8},
            {"name": "放松", "description": "深呼吸，敲打放松腿部肌肉", "reps": 5, "duration_sec": 60, "order_index": 9},
        ]
    },
    {
        "title": "坐姿腿举训练",
        "description": "坐着进行的腿部训练，安全简单，适合行动不便的老年人。",
        "difficulty": 2,
        "duration_min": 10,
        "exercises": [
            {"name": "热身", "description": "脚尖脚跟交替点地", "reps": 20, "duration_sec": 60, "order_index": 1},
            {"name": "坐姿抬腿", "description": "坐直，双腿抬起伸直保持3秒", "reps": 10, "duration_sec": 90, "order_index": 2},
            {"name": "坐姿腿开合", "description": "坐直，双腿开合训练大腿内侧", "reps": 15, "duration_sec": 90, "order_index": 3},
            {"name": "坐姿脚尖点地", "description": "交替用脚尖点地，锻炼小腿", "reps": 20, "duration_sec": 60, "order_index": 4},
            {"name": "坐姿膝盖抗阻", "description": "双手撑椅子两侧，膝盖向上顶用力", "reps": 10, "duration_sec": 90, "order_index": 5},
            {"name": "坐姿转踝", "description": "转动手腕脚踝关节", "reps": 10, "duration_sec": 60, "order_index": 6},
        ]
    },
    {
        "title": "哑铃入门（2磅）",
        "description": "使用轻量哑铃进行全身力量训练入门，动作规范，适合初学者。",
        "difficulty": 2,
        "duration_min": 15,
        "exercises": [
            {"name": "热身", "description": "空手挥臂+踏步", "reps": 20, "duration_sec": 90, "order_index": 1},
            {"name": "哑铃肩举", "description": "双手握哑铃，缓慢上举过头", "reps": 10, "duration_sec": 120, "order_index": 2},
            {"name": "哑铃侧平举", "description": "双手握哑铃，侧平举至肩高", "reps": 10, "duration_sec": 120, "order_index": 3},
            {"name": "哑铃前平举", "description": "双手握哑铃，正前方平举", "reps": 10, "duration_sec": 90, "order_index": 4},
            {"name": "哑铃弯举", "description": "双手弯举至肩高，锻炼二头肌", "reps": 12, "duration_sec": 120, "order_index": 5},
            {"name": "哑铃臂伸展", "description": "单臂向后伸展，锻炼三头肌", "reps": 10, "duration_sec": 90, "order_index": 6},
            {"name": "哑铃划船", "description": "屈髋俯身，向后拉哑铃", "reps": 10, "duration_sec": 120, "order_index": 7},
            {"name": "哑铃深蹲", "description": "双手握哑铃，做轻量深蹲", "reps": 10, "duration_sec": 120, "order_index": 8},
            {"name": "哑铃提踵", "description": "双手握哑铃，踮脚尖站立", "reps": 15, "duration_sec": 90, "order_index": 9},
            {"name": "放松", "description": "深呼吸，手臂拉伸放松", "reps": 5, "duration_sec": 60, "order_index": 10},
        ]
    },
    {
        "title": "自重深蹲基础",
        "description": "利用自身重量进行深蹲训练，增强下肢力量和平衡能力。",
        "difficulty": 3,
        "duration_min": 15,
        "exercises": [
            {"name": "热身", "description": "原地踏步+关节活动", "reps": 30, "duration_sec": 120, "order_index": 1},
            {"name": "扶椅深蹲", "description": "双手扶椅，缓慢下蹲起立", "reps": 10, "duration_sec": 120, "order_index": 2},
            {"name": "标准深蹲", "description": "双脚与肩同宽，屈髋屈膝下蹲", "reps": 10, "duration_sec": 150, "order_index": 3},
            {"name": "深蹲停顿", "description": "下蹲至最低点停顿2秒后站起", "reps": 8, "duration_sec": 120, "order_index": 4},
            {"name": "交替弓步", "description": "前后交替弓步，保持平衡", "reps": 12, "duration_sec": 150, "order_index": 5},
            {"name": "深蹲起立抬手", "description": "深蹲站起后双手上举", "reps": 10, "duration_sec": 120, "order_index": 6},
            {"name": "靠墙深蹲", "description": "背靠墙，屈膝下蹲保持30秒", "reps": 5, "duration_sec": 150, "order_index": 7},
            {"name": "放松拉伸", "description": "腿部拉伸放松", "reps": 5, "duration_sec": 90, "order_index": 8},
        ]
    },
    {
        "title": "墙壁俯卧撑进阶",
        "description": "在墙壁俯卧撑基础上的进阶训练，增加强度和挑战。",
        "difficulty": 3,
        "duration_min": 12,
        "exercises": [
            {"name": "热身", "description": "肩部+手腕活动", "reps": 15, "duration_sec": 90, "order_index": 1},
            {"name": "墙壁俯卧撑", "description": "身体倾斜角度更大", "reps": 12, "duration_sec": 120, "order_index": 2},
            {"name": "窄距墙壁俯卧撑", "description": "双手间距缩小，锻炼三头肌", "reps": 10, "duration_sec": 120, "order_index": 3},
            {"name": "单手墙壁俯卧撑", "description": "一只手背后，另一只手撑墙", "reps": 6, "duration_sec": 120, "order_index": 4},
            {"name": "墙壁扑跳", "description": "快速推离墙壁再接住", "reps": 8, "duration_sec": 90, "order_index": 5},
            {"name": "墙壁俯卧撑保持", "description": "下压后保持5秒", "reps": 8, "duration_sec": 120, "order_index": 6},
        ]
    },
    {
        "title": "弹力带全身组合",
        "description": "综合性弹力带训练，覆盖全身主要肌群，提升整体力量。",
        "difficulty": 3,
        "duration_min": 18,
        "exercises": [
            {"name": "全身热身", "description": "弹力带拉伸热身", "reps": 15, "duration_sec": 120, "order_index": 1},
            {"name": "弹力带深蹲推肩", "description": "深蹲+推肩组合", "reps": 10, "duration_sec": 150, "order_index": 2},
            {"name": "弹力带伐木", "description": "对角线旋转挥砍动作", "reps": 12, "duration_sec": 120, "order_index": 3},
            {"name": "弹力带硬拉", "description": "屈髋俯身拉弹力带", "reps": 12, "duration_sec": 150, "order_index": 4},
            {"name": "弹力带站姿划船", "description": "单臂站姿划船", "reps": 10, "duration_sec": 120, "order_index": 5},
            {"name": "弹力带深蹲侧移", "description": "深蹲+侧向移动", "reps": 16, "duration_sec": 150, "order_index": 6},
            {"name": "弹力带前踢腿", "description": "站立前踢弹力带", "reps": 12, "duration_sec": 120, "order_index": 7},
            {"name": "弹力带后踢腿", "description": "手扶墙后踢腿", "reps": 12, "duration_sec": 120, "order_index": 8},
            {"name": "弹力带胸部推", "description": "仰卧推弹力带", "reps": 12, "duration_sec": 120, "order_index": 9},
            {"name": "弹力带俄罗斯转体", "description": "坐姿转体拉弹力带", "reps": 20, "duration_sec": 120, "order_index": 10},
            {"name": "弹力带背伸展", "description": "俯卧背伸展", "reps": 12, "duration_sec": 90, "order_index": 11},
            {"name": "全身放松", "description": "深呼吸全身放松", "reps": 5, "duration_sec": 90, "order_index": 12},
        ]
    },
    {
        "title": "平衡与稳定训练",
        "description": "专门针对平衡感和本体感觉的训练，预防跌倒，提升生活质量。",
        "difficulty": 3,
        "duration_min": 15,
        "exercises": [
            {"name": "热身", "description": "原地踏步+平衡站立", "reps": 30, "duration_sec": 120, "order_index": 1},
            {"name": "单腿站立", "description": "扶椅单腿站立各30秒", "reps": 4, "duration_sec": 120, "order_index": 2},
            {"name": "脚跟脚尖走", "description": "脚跟走直线+脚尖走直线", "reps": 20, "duration_sec": 150, "order_index": 3},
            {"name": "平衡板站立", "description": "使用平衡板或折叠毛巾单脚站立", "reps": 6, "duration_sec": 120, "order_index": 4},
            {"name": "行走变向", "description": "直线行走+突然变向", "reps": 15, "duration_sec": 150, "order_index": 5},
            {"name": "串联行走", "description": "脚跟接脚尖直线行走", "reps": 20, "duration_sec": 150, "order_index": 6},
            {"name": "坐站交替", "description": "快速坐站交替", "reps": 12, "duration_sec": 120, "order_index": 7},
            {"name": "侧向跨步", "description": "横向跨步单脚站立", "reps": 16, "duration_sec": 150, "order_index": 8},
            {"name": "平衡深蹲", "description": "单腿浅蹲", "reps": 8, "duration_sec": 120, "order_index": 9},
            {"name": "放松平衡", "description": "站立深呼吸，闭眼平衡", "reps": 5, "duration_sec": 90, "order_index": 10},
        ]
    },
]


def seed_courses():
    """Seed the database with initial courses."""
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    sync_engine = create_engine(settings.SYNC_DATABASE_URL)
    
    # Create tables
    Base.metadata.create_all(sync_engine)
    
    with Session(sync_engine) as session:
        # Check if courses already exist
        result = session.execute(text("SELECT COUNT(*) FROM courses"))
        count = result.scalar()
        if count > 0:
            print(f"Courses already exist ({count}), skipping seed.")
            return
        
        for course_data in COURSES_DATA:
            exercises_data = course_data.pop("exercises")
            course = Course(**course_data)
            session.add(course)
            session.flush()
            
            for ex_data in exercises_data:
                exercise = Exercise(course_id=course.id, **ex_data)
                session.add(exercise)
        
        session.commit()
        print(f"Seeded {len(COURSES_DATA)} courses successfully!")


if __name__ == "__main__":
    seed_courses()