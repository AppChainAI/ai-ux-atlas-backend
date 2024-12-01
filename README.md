# AI UX Atlas Backend

AI UX Atlas：AI 驱动的用户体验地图生成工具 Mapping User Journeys with AI.

## 项目结构

```text
.
├── README.md
├── app
│   ├── __init__.py
│   ├── main.py
│   └── routes
│       ├── __init__.py
│       └── user_journeys.py
```

## 运行

使用 uv 运行

```shell
uv run app/main.py
```

## Docker 部署

```shell
docker build -t aiux-atlas-backend .
docker run -d --name aiux-atlas-backend -p 8000:8000 aiux-atlas-backend
```
