# Ageless Strength - AI Strength Training APP

欧美市场 55+ 老人居家力量训练 + AI姿态检测 + 家庭账号 + 订阅制

**欧美品牌名：Ageless Strength** | Strength Training for Every Age

## 项目状态

**Phase 1-2 ✅ 完成** | 等待Windows验证 | Phase 3-6 待完成

---

## 🚀 Windows上快速启动（3步搞定）

### 第一步：启动后端

```bash
# 进入后端目录
cd "C:\Users\admin\Desktop\订餐系统客户项目\大雄烧烤店订餐系统开发\senior-strength-app\backend"

# 双击运行（或在PowerShell中运行）
start.bat
```

**自动完成：**
- 创建Python虚拟环境
- 安装所有依赖（fastapi、sqlalchemy等）
- 初始化SQLite数据库（10节课程数据）
- 启动服务在 http://localhost:8000

**看到以下内容说明成功：**
```
 服务已启动！
 API文档：http://localhost:8000/docs
```

---

### 第二步：测试后端API

新开一个PowerShell窗口：

```bash
cd "C:\Users\admin\Desktop\订餐系统客户项目\大雄烧烤店订餐系统开发\senior-strength-app\backend"

python test_api.py
```

**应该看到全部测试通过 ✅**

---

### 第三步：启动Flutter APP

```bash
cd "C:\Users\admin\Desktop\订餐系统客户项目\大雄烧烤店订餐系统开发\senior-strength-app\frontend"

# 双击运行
run.bat
```

或者用VS Code打开 `senior-strength-app/frontend` 文件夹，按F5运行。

---

## 📁 项目结构

```
senior-strength-app/
├── SPEC.md              # 产品规格说明书
├── ARCHITECTURE.md      # 技术架构文档
├── README.md            # 本文件
├── backend/
│   ├── requirements.txt  # Python依赖
│   ├── start.bat         # Windows一键启动后端
│   ├── test_api.py # API测试脚本
│   ├── seed_data.py      # 种子数据
│   ├── .env.example      # 环境变量模板
│   └── app/
│       ├── main.py      # FastAPI入口
│       ├── core/        # 核心模块
│       ├── db/          # 数据库（SQLite）
│       ├── models/      # 数据模型
│       ├── schemas/     # Pydantic schemas
│       └── api/v1/endpoints/  # API端点
└── frontend/
    ├── run.bat          # Windows一键启动Flutter
    ├── pubspec.yaml     # Flutter依赖
    └── lib/ # Flutter源代码
```

---

##🔧 技术细节

### 后端（Python + FastAPI）
- **数据库**：SQLite（本地文件，不用装数据库服务）
- **认证**：JWT Token
- **无外部依赖**：PostgreSQL/Redis等都可选，不需要安装
- **API文档**：http://localhost:8000/docs

### 前端（Flutter）
- **状态管理**：Riverpod
- **视频播放**：video_player + chewie
- **AI姿态**：MediaPipe（待集成）
- **目标平台**：iOS + Android

---

## ❓常见问题

**Q:提示"未找到Python"**
A: 下载安装Python3.11+: https://www.python.org/downloads/

**Q: 提示"未找到Flutter"**
A: 下载安装Flutter: https://docs.flutter.dev/get-started/install

**Q: 后端启动报错"Port 8000被占用"**
A: 关闭占用8000端口的程序，或修改backend/main.py中的端口

**Q: Flutter编译报错**
A: 确保已运行 `flutter pub get`

---

## 📋 账号申请（最后一步）

等功能全部验证通过后，再申请：

| 账号 | 用途 | 费用 |
|------|------|------|
| Apple Developer | iOS上架 | $99/年 |
| Google Play | Android上架 | $25一次性 |
| Stripe | 真实收款 | 免费（收交易费） |

---

## 开发团队分工

| 角色 | 负责 |
|------|------|
| **你（老头儿）** | Windows上运行测试 + 最终账号申请上架 |
| **我（大胖儿）** | 所有代码开发 |

---

## 里程碑

| Phase | 内容 | 状态 |
|-------|------|------|
| P0 | 架构设计 | ✅ |
| P1 | 后端API + SQLite | ✅ |
| P2 | Flutter老人端核心 | ✅ |
| P3 | 子女端 + 家庭体系 | 🔜 下一步 |
| P4 | AI姿态检测 | 待开始 |
| P5 | 订阅系统 + Stripe | 待开始 |
| P6 | 测试 + 构建 + 上架 | 待开始 |

---

*最后更新：2026-06-11*