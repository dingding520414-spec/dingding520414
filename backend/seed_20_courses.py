#!/usr/bin/env python3
"""
Ageless Strength 20 Courses Database Seeder
运行此脚本更新数据库到20节课程完整版本

使用方法:
    cd backend
    python seed_20_courses.py
"""

import sqlite3
import uuid
from datetime import datetime

DATABASE_PATH = 'data/seniorstrength.db'
VIDEO_BASE = '/home/admin1234/.openclaw/workspace/projects/senior-strength-app/videos'

def get_now():
    return datetime.utcnow().isoformat()

def seed_courses(conn):
    """添加20节课程"""
    cur = conn.cursor()
    
    courses_data = [
        # 难度1 - 入门 (4节)
        ('全身拉伸放松', '训练后全身拉伸放松，改善柔韧性和恢复', 1, 15, f'{VIDEO_BASE}/11_full_body_stretch.mp4'),
        ('墙壁俯卧撑', '利用墙壁进行俯卧撑训练，强度适中，适合老年人增强上肢力量', 1, 10, f'{VIDEO_BASE}/02_wall_pushup.mp4'),
        ('椅子深蹲入门', '专为老年人设计的入门级深蹲训练，利用椅子作为支撑，确保安全', 1, 10, f'{VIDEO_BASE}/01_chair_squat.mp4'),
        ('臀桥训练', '臀桥动作练习，有效激活臀部和大腿后侧肌群', 1, 10, f'{VIDEO_BASE}/13_glute_bridge.mp4'),
        
        # 难度2 - 基础 (10节)
        ('哑铃入门（2磅）', '使用轻量哑铃进行全身力量训练入门，动作规范，适合初学者', 2, 15, f'{VIDEO_BASE}/06_dumbbell_shoulder.mp4'),
        ('哑铃肩部推举', '坐姿或站姿哑铃推举，增强肩部力量', 2, 12, f'{VIDEO_BASE}/14_dumbbell_shoulder_press.mp4'),
        ('坐姿划船训练', '使用弹力带或哑铃进行坐姿划船，锻炼背部肌群', 2, 12, f'{VIDEO_BASE}/15_seated_row.mp4'),
        ('坐姿腿举训练', '坐着进行的腿部训练，安全简单，适合行动不便的老年人', 2, 10, f'{VIDEO_BASE}/05_seated_leg_raise.mp4'),
        ('平板支撑入门', '学习正确的平板支撑姿势，强化核心肌群', 2, 10, f'{VIDEO_BASE}/16_plank_basic.mp4'),
        ('弓箭步训练', '前后弓箭步和侧弓箭步，提升下肢力量和平衡', 2, 10, f'{VIDEO_BASE}/17_lunges.mp4'),
        ('弹力带手臂训练', '使用弹力带进行上肢力量训练，增强手臂和肩部肌肉', 2, 12, f'{VIDEO_BASE}/03_resistance_band_bicep.mp4'),
        ('弹力带背部训练', '弹力带坐姿下拉和划船，改善圆肩和背部姿态', 2, 12, f'{VIDEO_BASE}/18_resistance_band_back.mp4'),
        ('弹力带腿部训练', '专门针对下肢的力量训练，增强腿部肌肉，预防跌倒', 2, 12, f'{VIDEO_BASE}/04_resistance_band_legcurl.mp4'),
        ('核心稳定训练', '死虫、鸟狗等动作，增强核心控制和身体稳定', 2, 15, f'{VIDEO_BASE}/19_core_stability.mp4'),
        
        # 难度3 - 进阶 (6节)
        ('墙壁俯卧撑进阶', '在墙壁俯卧撑基础上的进阶训练，增加强度和挑战', 3, 12, f'{VIDEO_BASE}/08_wall_pushup_advanced.mp4'),
        ('平衡与稳定训练', '专门针对平衡感和本体感觉的训练，预防跌倒', 3, 15, f'{VIDEO_BASE}/10_balance_training.mp4'),
        ('平衡挑战进阶', '单腿站立、跟脚走等进阶平衡训练', 3, 12, f'{VIDEO_BASE}/20_balance_advanced.mp4'),
        ('弹力带全身组合', '综合性弹力带训练，覆盖全身主要肌群', 3, 18, f'{VIDEO_BASE}/09_resistance_band_fullbody.mp4'),
        ('弹力带肩部训练', '利用弹力带进行肩部环绕和推举，增强肩部稳定性', 3, 12, f'{VIDEO_BASE}/21_resistance_band_shoulder.mp4'),
        ('自重深蹲基础', '利用自身重量进行深蹲训练，增强下肢力量', 3, 15, f'{VIDEO_BASE}/07_bodyweight_squat.mp4'),
    ]
    
    now = get_now()
    
    for title, desc, diff, dur, video_url in courses_data:
        # 检查是否已存在
        cur.execute('SELECT id FROM courses WHERE title = ?', (title,))
        existing = cur.fetchone()
        
        if existing:
            # 更新现有课程
            cur.execute('''
                UPDATE courses 
                SET description = ?, difficulty = ?, duration_min = ?, video_url = ?, is_active = 1
                WHERE title = ?
            ''', (desc, diff, dur, video_url, title))
            print(f'  更新: {title}')
        else:
            # 添加新课程
            cid = str(uuid.uuid4())
            cur.execute('''
                INSERT INTO courses (id, title, description, difficulty, duration_min, video_url, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            ''', (cid, title, desc, diff, dur, video_url, now))
            print(f'  新增: {title}')
    
    conn.commit()

def seed_exercises(conn):
    """添加课程动作"""
    cur = conn.cursor()
    
    # 获取课程ID映射
    cur.execute('SELECT id, title FROM courses')
    course_map = {title: cid for cid, title in cur.fetchall()}
    
    exercises_data = {
        '全身拉伸放松': [
            ('颈部前后拉伸', '缓慢将头向前向后倾斜', 3, 30),
            ('颈部左右拉伸', '将头侧向肩膀', 3, 30),
            ('肩部环绕', '双臂做画圈运动', 3, 30),
            ('手臂交叉拉伸', '交替拉伸左右手臂', 3, 30),
            ('体侧拉伸', '双手举过头顶向侧弯', 3, 30),
            ('股四头肌拉伸', '站立扶墙拉伸大腿前侧', 3, 30),
            ('小腿拉伸', '弓箭步后腿拉伸', 3, 30),
            ('髋部拉伸', '坐姿蝴蝶式展开', 3, 30),
        ],
        '臀桥训练': [
            ('仰卧臀桥', '平躺屈膝抬臀', 3, 45),
            ('单腿臀桥', '抬一条腿做臀桥', 3, 10),
            ('臀桥保持', '在顶端保持3秒', 3, 30),
            ('臀桥行走', '交替抬腿前进', 3, 45),
            ('臀桥收缩', '在顶端用力收紧臀部', 3, 30),
        ],
        '哑铃肩部推举': [
            ('坐姿哑铃推举', '双手握哑铃向上推', 3, 12),
            ('哑铃前平举', '向前抬起双臂', 3, 12),
            ('哑铃侧平举', '向两侧抬起双臂', 3, 12),
            ('哑铃俯卧飞鸟', '俯卧双手向两侧打开', 3, 12),
            ('哑铃耸肩', '双肩向上耸动', 3, 15),
            ('组合动作', '前平举+侧平举+推举', 3, 12),
        ],
        '坐姿划船训练': [
            ('弹力带划船', '坐姿拉弹力带至腹部', 3, 15),
            ('单臂划船', '单手交替划船', 3, 12),
            ('俯身划船', '身体前倾做划船动作', 3, 12),
            ('反向飞鸟', '双臂向后展开', 3, 15),
            ('肩胛收缩', '用力收缩肩胛骨', 3, 15),
            ('拉伸放松', '向前伸展背肌', 3, 30),
        ],
        '平板支撑入门': [
            ('标准平板支撑', '保持身体成直线', 3, 30),
            ('跪姿平板支撑', '膝盖着地减小难度', 3, 45),
            ('侧平板支撑', '身体侧向支撑', 3, 20),
            ('平板支撑保持', '在姿势中保持', 3, 30),
            ('臀部上下移动', '平板姿势中上下动', 3, 20),
        ],
        '弓箭步训练': [
            ('前后弓箭步', '向前向后迈步', 3, 12),
            ('侧弓箭步', '向侧方迈步', 3, 12),
            ('后退弓箭步', '单腿向后迈步', 3, 10),
            ('弓箭步保持', '在弓箭步姿势保持', 3, 20),
            ('交替弓箭步', '左右交替进行', 3, 12),
        ],
        '弹力带背部训练': [
            ('弹力带下拉', '双手向下拉弹力带', 3, 15),
            ('弹力带划船', '向后拉弹力带', 3, 15),
            ('弹力带外旋', '手臂外旋打开', 3, 12),
            ('弹力带耸肩', '向上耸肩', 3, 15),
            ('坐姿弹力带拉伸', '双手向前伸展', 3, 15),
        ],
        '核心稳定训练': [
            ('死虫动作', '仰卧交替伸展四肢', 3, 12),
            ('鸟狗动作', '四肢支撑交替伸展', 3, 12),
            ('平板支撑', '保持身体稳定', 3, 45),
            ('卷腹', '仰卧起身收缩腹肌', 3, 15),
            ('俄语转体', '坐姿左右转体', 3, 20),
            ('平衡球支撑', '在球上保持稳定', 3, 30),
        ],
        '平衡挑战进阶': [
            ('单腿站立', '单腿站立保持平衡', 3, 30),
            ('跟脚走', '脚跟接脚尖直线走', 3, 20),
            ('脚尖走', '用脚尖走直线', 3, 20),
            ('平衡木行走', '模拟走平衡木', 3, 30),
            ('单腿站立抬手', '单腿站立时向各方向抬手', 3, 15),
            ('闭眼单腿站', '闭眼单腿站立', 3, 15),
        ],
        '弹力带肩部训练': [
            ('弹力带推举', '双手向上推弹力带', 3, 15),
            ('弹力带前平举', '双臂向前抬起', 3, 12),
            ('弹力带侧平举', '双臂向两侧抬起', 3, 12),
            ('弹力带环绕', '双臂做肩部环绕', 3, 15),
            ('弹力带外旋', '手臂向外旋转', 3, 12),
            ('弹力带耸肩', '双肩向上耸动', 3, 15),
            ('组合推举', '推举+前举+侧举组合', 3, 12),
        ],
    }
    
    now = get_now()
    total_added = 0
    
    for title, exercises in exercises_data.items():
        course_id = course_map.get(title)
        if not course_id:
            print(f'  警告: 找不到课程 {title}')
            continue
        
        # 删除现有动作
        cur.execute('DELETE FROM exercises WHERE course_id = ?', (course_id,))
        
        # 添加新动作
        for order, (name, desc, sets, duration) in enumerate(exercises, 1):
            eid = str(uuid.uuid4())
            cur.execute('''
                INSERT INTO exercises (id, course_id, name, description, reps, duration_sec, video_url, order_index, created_at)
                VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?)
            ''', (eid, course_id, name, desc, sets, duration, order, now))
            total_added += 1
        
        print(f'  添加动作: {title} ({len(exercises)}个)')
    
    conn.commit()
    print(f'  共添加 {total_added} 个动作')

def main():
    print('=== Ageless Strength 20 Courses 数据库更新 ===\n')
    
    conn = sqlite3.connect(DATABASE_PATH)
    
    print('1. 更新课程数据...')
    seed_courses(conn)
    
    print('\n2. 添加课程动作...')
    seed_exercises(conn)
    
    # 验证
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM courses')
    course_count = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM exercises')
    exercise_count = cur.fetchone()[0]
    
    print(f'\n=== 验证结果 ===')
    print(f'课程数: {course_count}')
    print(f'动作数: {exercise_count}')
    print('✅ 数据库更新完成!')
    
    conn.close()

if __name__ == '__main__':
    main()
