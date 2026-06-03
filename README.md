# 暖爪救助

流浪宠物综合救助管理平台课程原型，前后端分离：**Django + Django REST Framework + JWT** 后端，**React** 前端。

## 功能概览

| 模块 | 说明 |
|------|------|
| 用户与认证 | 注册、登录、个人资料、隐私协议、找回密码 |
| 门户 | 首页轮播 |
| 领养宠物 | 宠物档案、领养申请与审核 |
| 科普公告 | CMS 文章、收藏 |
| 报失寻主 | 寻宠/招领发布、列表与详情 |
| 社区交流 | 帖子、评论、点赞、收藏 |
| 救助追踪 | 救助案例上报与状态流转 |
| 管理后台 | 用户/内容/领养等管理 |
| AI 辅助 | 品种识图、领养文案生成（需配置） |

## 技术栈

- **后端**：Django 4.2+、DRF、SimpleJWT、MySQL（默认）或 SQLite、Pillow、可选 PyTorch 品种模型
- **前端**：React、React Router、Axios、Bootstrap

## 环境要求

- Python 3.10+（建议 3.11）
- Node.js 18+
- MySQL 8+（本地开发可改用 SQLite，见下文）
- Git

## 快速开始

### 1. 克隆仓库

```bash
git clone <你的仓库地址>
cd pet-connect-web
```

### 2. 后端

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

复制环境变量并按需修改（在 `backend` 目录创建 `.env`）：

```env
SECRET_KEY=请换成随机长字符串
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 使用 SQLite 时可设（无需 MySQL）
USE_SQLITE=true

# 使用 MySQL 时配置（USE_SQLITE 不设或 false）
DB_NAME=pet_rescue
DB_USER=root
DB_PASSWORD=你的密码
DB_HOST=127.0.0.1
DB_PORT=3306
```

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

API 根地址：`http://localhost:8000/api/`

### 3. 前端

新开终端：

```powershell
cd frontend
npm install
```

在 `frontend` 下创建 `.env.local`：

```env
REACT_APP_API_BASE_URL=http://localhost:8000/api
```

```powershell
npm start
```

浏览器访问：`http://localhost:3000`

## 品种识别模型（可选）

权重文件较大，默认不纳入 Git。克隆后可在项目根目录执行：

```powershell
backend\venv\Scripts\python.exe scripts\download_breed_model.py
```

或按 `scripts/` 内说明自行训练。未下载时品种识别相关接口可能不可用，其余功能不受影响。

## 中文源码编码（Windows 必看）

含中文的源码须为 **UTF-8（无 BOM）**。若页面出现乱码，在项目根目录执行：

```powershell
backend\venv\Scripts\python.exe scripts\ensure_utf8.py
```

然后重启前端并强制刷新浏览器（`Ctrl + F5`）。编辑器请使用 UTF-8 保存（可参考根目录 `.editorconfig`）。

## 勿提交到 Git 的内容

- `backend/venv/`、`frontend/node_modules/`
- `.env`、`.env.local` 等含密钥的文件
- `backend/media/` 上传目录、`db.sqlite3`（若使用）
- `backend/ml/breed_classifier.pt`、`backend/ml/data/` 等大文件

详见 `.gitignore`。

## 目录结构

```
pet-connect-web/
├── backend/              # Django 后端
│   ├── accounts/         # 用户与资料
│   ├── pets/             # 领养宠物
│   ├── lostfound/        # 报失寻主
│   ├── rescue/           # 救助追踪
│   ├── community/        # 社区
│   ├── cms/              # 科普公告
│   ├── portal/           # 门户轮播
│   ├── system/           # 管理、AI 等
│   ├── common/           # 上传、品种识别等
│   ├── requirements.txt
│   └── manage.py
├── frontend/             # React 前端
│   └── src/
│       ├── pages/
│       ├── components/
│       └── api/
├── scripts/              # UTF-8 检查、模型脚本等
├── .env.example
└── README.md
```

## 协作说明

- 依赖安装以 **`backend/requirements.txt`** 为准，勿在仓库根目录再放一份 `pip freeze` 列表。
- 拉取代码后执行 `migrate`，报失寻主、救助上报等需 `lostfound`、`rescue` 的位置相关迁移。
- 管理员账号通过 `createsuperuser` 创建；演示数据可用 `seed_demo`。

## 许可证与课程说明

本项目为工程实践课程第七组原型，仅供学习与演示使用。
