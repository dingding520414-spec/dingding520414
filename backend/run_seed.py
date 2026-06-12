import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.models.models import Course, Exercise, Base
from app.core.config import get_settings

settings = get_settings()

COURSES_DATA = [
    {
        "title": "椅子深蹲入门",
        "description": "专为老年人设计的入门级深蹲训练，利用椅子作为支撑，确保安全。",
        "difficulty": 1,
        "duration_min": 10,
        "exercises": [
            {"name": "热身 - 关节活动", "description": "缓慢转动手腕、脚踝、膝盖和髋关节", "reps": 10, "duration_sec": 120, "order_index": 1},
            {"name": "扶椅站立", "description": "双手扶椅，缓慢坐下再站起，保持平衡", "reps": 8, "duration_sec": 120, "order_index": 2},
            {"name": "半深蹲", "description": "扶椅，下蹲至膝盖弯曲约45度", "reps": 8, "duration_sec": 120, "order_index": 3},
            {"name": "踮脚站立", "description": "扶椅，踮起脚尖保持3秒", "reps": 10, "duration_sec": 90, "order_index": 4},
            {"name": "侧身抬腿", "description": "扶椅，侧抬右腿保持3秒", "reps": 8, "duration_sec": 120, "order_index": 5},
            {"name": "放松拉伸", "description": "站立深呼吸，手臂上举放松", "reps": 5, "duration_sec": 60, "order_index": 6},
        ]
    },
    {
        "title": "墙壁俯卧撑",
        "description": "利用墙壁进行俯卧撑训练，强度适中。",
        "difficulty": 1,
        "duration_min": 10,
        "exercises": [
            {"name": "热身 - 肩部活动", "description": "双手扶墙，画圈活动肩关节", "reps": 10, "duration_sec": 60, "order_index": 1},
            {"name": "墙壁俯卧撑", "description": "双手撑墙，身体倾斜15度", "reps": 10, "duration_sec": 120, "order_index": 2},
            {"name": "墙壁侧推", "description": "右手撑墙，左手推墙", "reps": 10, "duration_sec": 90, "order_index": 3},
            {"name": "墙壁夹背", "description": "双手撑墙，手肘夹紧身体", "reps": 10, "duration_sec": 90, "order_index": 4},
            {"name": "放松", "description": "深呼吸，双臂自然下垂", "reps": 5, "duration_sec": 60, "order_index": 5},
        ]
    },
    {
        "title": "弹力带手臂训练",
        "description": "使用弹力带进行上肢力量训练。",
        "difficulty": 2,
        "duration_min": 12,
        "exercises": [
            {"name": "热身", "description": "空手挥臂热身", "reps": 10, "duration_sec": 60, "order_index": 1},
            {"name": "弹力带二头弯举", "description": "双脚踩弹力带，双手弯举", "reps": 12, "duration_sec": 120, "order_index": 2},
            {"name": "弹力带肩推", "description": "弹力带放在身后，双手向上推举", "reps": 10, "duration_sec": 120, "order_index": 3},
            {"name": "弹力带划船", "description": "弹力带固定前方，双手向后拉伸", "reps": 12, "duration_sec": 120, "order_index": 4},
        ]
    },
    {
        "title": "弹力带腿部训练",
        "description": "专门针对下肢的力量训练。",
        "difficulty": 2,
        "duration_min": 12,
        "exercises": [
            {"name": "热身", "description": "原地踏步热身", "reps": 20, "duration_sec": 60, "order_index": 1},
            {"name": "弹力带深蹲", "description": "弹力带绕大腿，屈髋屈膝下蹲", "reps": 10, "duration_sec": 120, "order_index": 2},
            {"name": "弹力带腿弯举", "description": "站立，弹力带绕脚踝向后弯举", "reps": 12, "duration_sec": 90, "order_index": 3},
        ]
    },
    {
        "title": "坐姿腿举训练",
        "description": "坐着进行的腿部训练，安全简单。",
        "difficulty": 2,
        "duration_min": 10,
        "exercises": [
            {"name": "热身", "description": "脚尖脚跟交替点地", "reps": 20, "duration_sec": 60, "order_index": 1},
            {"name": "坐姿抬腿", "description": "坐直，双腿抬起伸直保持3秒", "reps": 10, "duration_sec": 90, "order_index": 2},
            {"name": "坐姿腿开合", "description": "坐直，双腿开合训练大腿内侧", "reps": 15, "duration_sec": 90, "order_index": 3},
        ]
    },
    {
        "title": "哑铃入门（2磅）",
        "description": "使用轻量哑铃进行全身力量训练入门。",
        "difficulty": 2,
        "duration_min": 15,
        "exercises": [
            {"name": "热身", "description": "空手挥臂+踏步", "reps": 20, "duration_sec": 90, "order_index": 1},
            {"name": "哑铃肩举", "description": "双手握哑铃，缓慢上举过头", "reps": 10, "duration_sec": 120, "order_index": 2},
            {"name": "哑铃侧平举", "description": "双手握哑铃，侧平举至肩高", "reps": 10, "duration_sec": 120, "order_index": 3},
        ]
    },
    {
        "title": "自重深蹲基础",
        "description": "利用自身重量进行深蹲训练。",
        "difficulty": 3,
        "duration_min": 15,
        "exercises": [
            {"name": "热身", "description": "原地踏步+关节活动", "reps": 30, "duration_sec": 120, "order_index": 1},
            {"name": "扶椅深蹲", "description": "双手扶椅，缓慢下蹲起立", "reps": 10, "duration_sec": 120, "order_index": 2},
            {"name": "标准深蹲", "description": "双脚与肩同宽，屈髋屈膝下蹲", "reps": 10, "duration_sec": 150, "order_index": 3},
        ]
    },
    {
        "title": "墙壁俯卧撑进阶",
        "description": "墙壁俯卧撑的进阶训练。",
        "difficulty": 3,
        "duration_min": 12,
        "exercises": [
            {"name": "热身", "description": "肩部+手腕活动", "reps": 15, "duration_sec": 90, "order_index": 1},
            {"name": "墙壁俯卧撑", "description": "身体倾斜角度更大", "reps": 12, "duration_sec": 120, "order_index": 2},
        ]
    },
    {
        "title": "弹力带全身组合",
        "description": "综合性弹力带训练，覆盖全身主要肌群。",
        "difficulty": 3,
        "duration_min": 18,
        "exercises": [
            {"name": "全身热身", "description": "弹力带拉伸热身", "reps": 15, "duration_sec": 120, "order_index": 1},
            {"name": "弹力带深蹲推肩", "description": "深蹲+推肩组合", "reps": 10, "duration_sec": 150, "order_index": 2},
        ]
    },
    {
        "title": "平衡与稳定训练",
        "description": "专门针对平衡感和本体感觉的训练。",
        "difficulty": 3,
        "duration_min": 15,
        "exercises": [
            {"name": "热身", "description": "原地踏步+平衡站立", "reps": 30, "duration_sec": 120, "order_index": 1},
            {"name": "单腿站立", "description": "扶椅单腿站立各30秒", "reps": 4, "duration_sec": 120, "order_index": 2},
        ]
    },
]

def seed_courses():
    os.makedirs(os.path.dirname(settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")), exist_ok=True)
    Base.metadata.create_all(settings.SYNC_DATABASE_URL.replace("sqlite:///", ""))

    engine = create_engine(settings.SYNC_DATABASE_URL, connect_args={"check_same_thread": False})
    with Session(engine) as session:
        result = session.execute(text("SELECT COUNT(*) FROM courses"))
        count = result.scalar()
        if count > 0:
            print(f"课程已存在 ({count})，跳过播种")
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
        print(f"✅ 成功播种 {len(COURSES_DATA)} 节课程")

if __name__ == "__main__":
    seed_courses()