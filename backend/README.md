# 暖爪救助 · 后端

Django REST API，详细安装与模块说明见仓库根目录 [README.md](../README.md)。

## 常用命令

```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## API 说明

- 路由入口：`api/urls.py` 及各 app 的 `urls.py`
- 除注册、登录等公开接口外，需在请求头携带：`Authorization: Bearer <token>`
- 上传接口使用 `multipart/form-data`
