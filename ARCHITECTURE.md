# ARCHITECTURE.md — 中老年力量训练APP 技术架构

## 1. 技术栈总览

| 层级 | 技术选型 | 版本 | 说明 |
|------|---------|------|------|
| **APP框架** | Flutter | 3.19+ | 跨平台iOS/Android |
| **AI姿态检测** | MediaPipe | 0.10+ | Google开源，实时姿态 |
| **后端框架** | FastAPI | 0.109+ | Python异步API |
| **数据库** | PostgreSQL | 15+ | 用户数据、进度数据 |
| **缓存** | Redis | 7+ | Session、速率限制 |
| **文件存储** | Cloudflare R2 | - | 视频/CDN（兼容S3协议） |
| **订阅管理** | RevenueCat | - | iOS/Android订阅+防流失 |
| **支付** | Stripe | - | 订阅收款 |
| **AI生成** | GPT-4o | - | 个性化营养建议生成 |
| **部署** | Railway / Render | - | 后端API托管 |

---

## 2. 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│老人端 APP (Flutter)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 视频课程 │  │ AI姿态   │  │ 打卡进度 │  │ 营养建议 │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼─────────────┼─────────────┼─────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                           │ HTTPS
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ 后端 API (FastAPI)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 用户模块 │  │ 课程模块 │  │ 训练模块 │  │ 订阅模块 │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│ │             │             │             │          │
│  ┌────┴─────────────┴─────────────┴─────────────┴────┐    │
│  │                    Service Layer                    │    │
│  └────────────────────────┬───────────────────────────┘    │
│                           │                                 │
│  ┌────────────────────────┴───────────────────────────┐    │
│  │              PostgreSQL + Redis + R2                 │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐ ┌──────────────┐   ┌──────────────┐
│ Cloudflare R2│   │  RevenueCat   │   │   Stripe     │
│  (视频存储)  │   │  (订阅管理)   │   │  (支付)      │
└──────────────┘   └──────────────┘   └──────────────┘
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐ ┌──────────────┐   ┌──────────────┐
│  CDN分发 │   │ App Store    │   │ 支付回调 │
│  (视频流)    │   │ Google Play  │   │ webhooks     │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## 3. 数据库设计

### 3.1 ER图核心实体

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   User      │       │   Family    │       │  Course     │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │←──────│ id (PK)     │       │ id (PK)     │
│ phone │ 1:N │ created_at │       │ title │
│ email       │       └─────────────┘       │ description │
│ name │              │1:N           │ difficulty │
│ age         │              │              │ duration_min│
│ gender │       ┌───────┴───────┐ │ video_url   │
│ fitness_goal│       │FamilyMember │       │ thumbnail │
│ created_at  │       ├──────────────┤       │ is_active │
└─────┬───────┘       │ id (PK)      │       └─────────────┘
      │               │ family_id(FK)│ │1:N
      │1:N            │ user_id (FK) │ │
      │               │ role         │     ┌──────┴──────┐
      │               │ added_at     │      │  Exercise   │
      │               └──────────────┘      ├─────────────┤
      │                                      │ id (PK)    │
      │              ┌─────────────┐       │ course_id  │
      │               │TrainingSession│     │ name │
      │              ├─────────────┤       │ description│
      │               │ id (PK)    │        │ reps │
      │               │ user_id(FK)│ │ duration_sec│
      │               │ course_id  │        │ video_time │
      │               │ started_at │        │ order      │
      │               │ completed_at│└─────────────┘
      │               │ duration_sec│
      │               │ ai_score   │
      │               └─────────────┘
      │
      │1:N
      │
┌─────┴───────┐ ┌─────────────┐
│Subscription│       │DailyCheckIn│
├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)    │
│ user_id(FK) │       │ user_id(FK)│
│ plan_type   │       │ date │
│ status      │       │ course_id  │
│ stripe_sub_id│      │ completed │
│ current_period_end││ created_at │
└─────────────┘       └─────────────┘
```

### 3.2 核心表结构

#### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    name VARCHAR(100),
    age INTEGER,
    gender VARCHAR(10),
    fitness_goal TEXT,
    health_notes TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### families
```sql
CREATE TABLE families (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### family_members
```sql
CREATE TABLE family_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id UUID REFERENCES families(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(20) CHECK (role IN ('elder', 'adult')),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(family_id, user_id)
);
```

#### courses
```sql
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 5),
    duration_min INTEGER,
    video_url TEXT,
    thumbnail_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### exercises
```sql
CREATE TABLE exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id),
    name VARCHAR(200),
    description TEXT,
    reps INTEGER,
    duration_sec INTEGER,
    video_timestamp INTEGER,
    order_index INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### training_sessions
```sql
CREATE TABLE training_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    course_id UUID REFERENCES courses(id),
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_sec INTEGER,
    ai_score INTEGER CHECK (ai_score BETWEEN 0 AND 100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### daily_checkins
```sql
CREATE TABLE daily_checkins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    checkin_date DATE NOT NULL,
    course_id UUID REFERENCES courses(id),
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, checkin_date)
);
```

#### subscriptions
```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    plan_type VARCHAR(20) CHECK (plan_type IN ('free', 'personal', 'family')),
    status VARCHAR(20) CHECK (status IN ('active', 'cancelled', 'expired')),
    stripe_subscription_id VARCHAR(255),
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 4. API 接口设计

### 4.1 认证模块
```
POST /api/v1/auth/register
    Request: { phone/email, password, name, age }
    Response: { user, access_token }

POST /api/v1/auth/login
    Request: { email, password }
    Response: { user, access_token }

POST /api/v1/auth/refresh
    Request: { refresh_token }
    Response: { access_token }
```

### 4.2 用户模块
```
GET /api/v1/users/me
    Response: { user }

PATCH /api/v1/users/me
    Request: { name?, age?, gender?, fitness_goal?, health_notes? }
    Response: { user }

POST /api/v1/users/avatar
    Request: multipart/form-data (image)
    Response: { avatar_url }
```

### 4.3 课程模块
```
GET  /api/v1/courses
    Query: { difficulty?, limit?, offset? }
    Response: { courses: [...], total }

GET  /api/v1/courses/{id}
    Response: { course, exercises: [...] }
```

### 4.4 训练模块
```
POST /api/v1/training/start
    Request: { course_id }
    Response: { session_id, start_time }

POST /api/v1/training/{session_id}/complete
    Request: { duration_sec, ai_score }
    Response: { session, checkin }

POST /api/v1/training/{session_id}/ai-feedback
    Request: { exercise_id, video_segment_base64 }
    Response: { score, feedback_text }
```

### 4.5 进度模块
```
GET  /api/v1/progress/weekly
    Query: { user_id? } (自己或绑定的老人)
    Response: { checkins: [...], total_duration, streak_days }

GET  /api/v1/progress/monthly
    Query: { user_id?, month? }
    Response: { report_url } (PDF)
```

### 4.6 家庭模块
```
POST /api/v1/family/generate-code
    Response: { bind_code, expires_at }

POST /api/v1/family/bind
    Request: { bind_code }
    Response: { family_members: [...] }

GET  /api/v1/family/members
    Response: { family_members: [...] }

GET  /api/v1/family/progress/{elder_id}
    Response: { weekly_progress }
```

### 4.7 订阅模块
```
POST /api/v1/subscription/create
    Request: { plan_type }
    Response: { stripe_payment_url }

POST /api/v1/subscription/cancel
    Response: { subscription }

GET /api/v1/subscription/status
    Response: { subscription, plan_type, current_period_end }

POST /api/v1/webhooks/stripe
    Stripe回调处理
```

---

## 5. Flutter APP架构

### 5.1 项目结构
```
lib/
├── main.dart
├── app.dart
├── core/
│   ├── constants/
│   │   ├── app_colors.dart
│   │   ├── app_typography.dart
│   │   └── app_spacing.dart
│   ├── theme/
│   │   └── app_theme.dart
│   ├── utils/
│   │   └── validators.dart
│   └── network/
│       ├── api_client.dart
│       └── api_endpoints.dart
├── data/
│   ├── models/
│   │   ├── user.dart
│   │   ├── course.dart
│   │   ├── training_session.dart
│   │   └── subscription.dart
│   ├── repositories/
│   │   ├── auth_repository.dart
│   │   ├── course_repository.dart
│   │   ├── training_repository.dart
│   │   └── family_repository.dart
│   └── services/
│       ├── api_service.dart
│       └── storage_service.dart
├── domain/
│   ├── entities/
│   └── usecases/
├── presentation/
│   ├── pages/
│   │   ├── elder/
│   │   │   ├── home_page.dart
│   │   │   ├── course_list_page.dart
│   │   │   ├── training_page.dart
│   │   │   ├── progress_page.dart
│   │   │   └── profile_page.dart
│   │   └── adult/
│   │       ├── family_dashboard_page.dart
│   │       ├── progress_view_page.dart
│   │       └── subscription_page.dart
│   ├── widgets/
│   │   ├── course_card.dart
│   │   ├── exercise_timer.dart
│   │   ├── ai_pose_overlay.dart
│   │   ├── checkin_button.dart
│   │   └── progress_chart.dart
│   └── providers/
│       ├── auth_provider.dart
│       ├── course_provider.dart
│       ├── training_provider.dart
│       └── family_provider.dart
└── ml/
    └── pose_detector.dart (MediaPipe集成)
```

### 5.2 状态管理：Riverpod
- 所有数据层通过 Riverpod Provider 管理
- 异步请求使用 AsyncNotifier
- 家庭共享状态通过 StateNotifier

### 5.3 AI姿态检测集成
```dart
// 使用MediaPipe Pose Detection
class PoseDetector {
  final PoseCamera _camera;
  final List<PoseLandmark> _landmarks;
  
  // 检测关键点
  // 膝盖角度计算
  // 背部角度计算
  // 实时反馈生成
}
```

---

## 6. 部署架构

### 6.1 后端部署（Railway）
```
┌─────────────────────────────────────┐
│         Railway (美国区域)            │
│  ┌──────────────────────────────┐   │
│  │ FastAPI Application │   │
│  │  - gunicorn + uvicorn workers│   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │    PostgreSQL 15             │   │
│  │    (自带，或Railway Postgres)│   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │    Redis 7 │   │
│  │    (缓存+速率限制)           │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────┐   ┌─────────────────┐
│  Cloudflare R2  │    │ Stripe API │
│  (视频存储) │    │   (支付)       │
└─────────────────┘    └─────────────────┘
```

### 6.2 视频/CDN架构
```
用户播放视频请求
      │
      ▼
Cloudflare CDN (全球分发)
      │
      ▼
Cloudflare R2 (源站，存储原始视频)
```

### 6.3 环境变量配置
```
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
REVENUECAT_API_KEY=...
JWT_SECRET=...
R2_ACCOUNT_ID=...
R2_ACCESS_KEY=...
R2_SECRET_KEY=...
R2_BUCKET_NAME=...
```

---

## 7. 安全设计

### 7.1 认证
- JWT Access Token（15分钟）
- Refresh Token（7天）
- 密码bcrypt加密

### 7.2 HIPAA合规（医疗数据）
- 传输加密（HTTPS）
- 数据库加密（静态）
- 医疗报告数据脱敏
- Stripe不存储医疗数据

### 7.3 速率限制
- API：100请求/分钟
- 登录：5次/分钟
- 训练完成：10次/分钟

---

## 8. 监控与日志

| 组件 | 工具 |
|------|------|
| 错误追踪 | Sentry |
| 日志 | Railway Logs / Datadog |
| 性能监控 | Grafana (Railway内置) |
| 订阅监控 | RevenueCat Dashboard |

---

## 9. 开发计划（Phase 1-5）

| Phase | 内容 | 交付物 | 预计 |
|-------|------|--------|------|
| **P0** | 架构设计 | SPEC.md, ARCHITECTURE.md | Week 1 |
| **P1** | 后端API + 数据库 | 可运行API服务 | Week 2-3 |
| **P2** | Flutter老人端核心 | 可测试APP（老人端） | Week 4-6 |
| **P3** | 子女端 + 家庭体系 | 家庭账号可用 | Week 7-8 |
| **P4** | AI姿态检测 | AI功能上线 | Week 9-10 |
| **P5** | 订阅系统 + Stripe | 商业化能力 | Week 11-12 |
| **P6** | 测试 + 构建 + 自检 | IPA/APK + 上架文档 | Week 13-14 |

---

*文档版本：v1.0*
*创建时间：2026-06-11*
*状态：待确认后推进*