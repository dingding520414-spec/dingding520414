"""
Backend API测试脚本
在Windows PowerShell中运行：
python test_api.py
"""
import httpx
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("\n[测试1] 健康检查...")
    resp = httpx.get(f"{BASE_URL}/health")
    assert resp.status_code == 200, f"失败: {resp.status_code}"
    data = resp.json()
    print(f"  ✅ 服务正常 - 版本: {data.get('version')}")
    return data

def test_register():
    """测试用户注册"""
    print("\n[测试2] 用户注册...")
    resp = httpx.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "test123456",
        "name": "测试用户",
        "age": 65,
        "role": "elder"
    })
    assert resp.status_code == 200, f"失败: {resp.status_code}"
    data = resp.json()
    print(f"  ✅ 注册成功 - 用户: {data['user']['name']}")
    return data["access_token"]

def test_login(token):
    """测试登录"""
    print("\n[测试3] 用户登录...")
    resp = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "test123456"
    })
    assert resp.status_code == 200, f"失败: {resp.status_code}"
    data = resp.json()
    print(f"  ✅ 登录成功 - Token: {data['access_token'][:20]}...")
    return data["access_token"]

def test_courses(token):
    """测试获取课程列表"""
    print("\n[测试4] 获取课程列表...")
    resp = httpx.get(
        f"{BASE_URL}/api/v1/courses",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200, f"失败: {resp.status_code}"
    data = resp.json()
    print(f"  ✅ 课程数量: {data['total']}")
    for course in data['courses'][:3]:
        print(f"     - {course['title']} (难度: {course['difficulty']}星)")
    return data['courses'][0]['id']

def test_course_detail(token, course_id):
    """测试获取课程详情"""
    print("\n[测试5] 获取课程详情...")
    resp = httpx.get(
        f"{BASE_URL}/api/v1/courses/{course_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200, f"失败: {resp.status_code}"
    data = resp.json()
    print(f"  ✅ {data['title']}")
    print(f"     动作数量: {len(data['exercises'])}")
    return data['exercises'][0]['id']

def test_training_flow(token, course_id, exercise_id):
    """测试训练流程"""
    print("\n[测试6] 训练流程...")
    
    # 开始训练
    resp = httpx.post(
        f"{BASE_URL}/api/v1/training/start",
        headers={"Authorization": f"Bearer {token}"},
        json={"course_id": str(course_id)}
    )
    assert resp.status_code == 200, f"开始训练失败: {resp.status_code}"
    session_id = resp.json()['session_id']
    print(f"  ✅ 开始训练 - Session: {session_id[:8]}...")
    
    # 完成训练
    time.sleep(1)
    resp = httpx.post(
        f"{BASE_URL}/api/v1/training/{session_id}/complete",
        headers={"Authorization": f"Bearer {token}"},
        json={"duration_sec": 300, "ai_score": 85}
    )
    assert resp.status_code == 200, f"完成训练失败: {resp.status_code}"
    print(f"  ✅ 完成训练 - 时长: 300秒, AI评分: 85")
    
    # 获取AI反馈
    resp = httpx.post(
        f"{BASE_URL}/api/v1/training/{session_id}/ai-feedback",
        headers={"Authorization": f"Bearer {token}"},
        json={"exercise_id": str(exercise_id)}
    )
    assert resp.status_code == 200, f"AI反馈失败: {resp.status_code}"
    data = resp.json()
    print(f"  ✅ AI反馈 -评分: {data['score']}, 建议: {data['feedback_text'][:30]}...")

def test_progress(token):
    """测试进度查询"""
    print("\n[测试7] 进度查询...")
    resp = httpx.get(
        f"{BASE_URL}/api/v1/training/progress/weekly",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200, f"失败: {resp.status_code}"
    data = resp.json()
    print(f"  ✅ 周进度 - 打卡次数: {len(data['checkins'])}, 连续天数: {data['streak_days']}")

def test_family(token):
    """测试家庭功能"""
    print("\n[测试8] 家庭绑定...")
    
    # 生成绑定码
    resp = httpx.post(
        f"{BASE_URL}/api/v1/family/generate-code",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200, f"失败: {resp.status_code}"
    bind_code = resp.json()['bind_code']
    print(f"  ✅ 绑定码: {bind_code}")

def main():
    print("=" * 50)
    print("  SeniorStrength API自动化测试")
    print("=" * 50)
    
    try:
        test_health()
        token = test_register()
        token = test_login(token)
        course_id = test_courses(token)
        exercise_id = test_course_detail(token, course_id)
        test_training_flow(token, course_id, exercise_id)
        test_progress(token)
        test_family(token)
        
        print("\n" + "=" * 50)
        print("  所有测试通过！✅")
        print("=" * 50)
        
    except httpx.ConnectError:
        print("\n[错误] 无法连接到后端服务")
        print("请先运行 start.bat 启动后端服务")
    except AssertionError as e:
        print(f"\n[错误] 测试失败: {e}")
    except Exception as e:
        print(f"\n[错误] {e}")

if __name__ == "__main__":
    main()