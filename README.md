# 萝卜岗识别（lobo）· 阶段 1

粘贴一份事业单位 / 国企招聘公告，AI（DeepSeek）按萝卜岗特征体系分析其疑似程度。

## 后端
1. `pip install -e ".[dev]"`
2. 复制 `.env.example` 为 `.env`，填入 `DEEPSEEK_API_KEY`
3. （可选）用 PostgreSQL：`docker compose up -d db`，并在 `.env` 设
   `DATABASE_URL=postgresql+psycopg2://lobo:lobo@localhost:5432/lobo`
   不设则默认使用本地 SQLite（`lobo.db`）。
4. 启动：`uvicorn app.main:app --reload`

## 前端
1. `cd frontend && npm install`
2. `npm run dev`，访问 http://localhost:5173

## 测试
- 单元测试（默认，无需 key）：`pytest`
- 金标准集成测试（需 key）：`pytest -m integration`

## 免责声明
分析结果由 AI 基于公开招聘文本自动推测，仅供参考，不构成确定性结论，不针对具体单位或个人。
