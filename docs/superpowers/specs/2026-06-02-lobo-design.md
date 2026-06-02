# 萝卜岗识别应用（lobo）设计文档

> 状态：已与用户对齐并批准（2026-06-02）
> 范围：本文档为整体设计 + 阶段 1（核心分析引擎）规格。后续阶段为概要。

## 1. 背景与问题

中国事业单位、国企招聘中存在"萝卜岗/萝卜招聘"现象——为内定人选量身定制招聘条件（专业、年龄、学历、经历、证书等设置得异常具体），使实际上只有特定一人符合，排挤其他竞争者。普通求职者难以辨别一个岗位是否被"内定"，存在严重的信息不对称。

## 2. 目标

面向公众的 Web 应用，收集全国事业单位、国企岗位，用 AI（DeepSeek）按一套"疑似萝卜岗"特征体系分析每个岗位，输出**疑似度评分 + 理由 + 高亮可疑条件**，帮助求职者识别、促进招聘公开透明。

终点为全国级产品，分 4 阶段落地。**阶段 1 先交付核心分析引擎**。

## 3. 关键产品决策

| 维度 | 决定 |
|------|------|
| 目标定位 | 全国级产品，分阶段落地 |
| 数据来源 | 爬虫铺量 + 用户众包补充 |
| 分析输出 | 疑似度评分(0-100 + 低/中/高) + 理由 + 高亮可疑条件 |
| 技术栈 | 全 Python（FastAPI），前端 Vue3 + Vite |
| 前端形态 | Web 响应式网站 |
| 大模型 | DeepSeek（境内合规、中文强、成本低） |
| 架构 | 方案 A：单体 + 异步任务队列（内部分层，未来可拆分） |
| 判定逻辑 | 以特征清单为主框架引导 DeepSeek（可解释、稳定） |
| 阶段 1 起点 | 先做分析引擎（粘贴公告 → 疑似度报告） |

## 4. 系统架构（最终形态）

**五层模块（FastAPI 单体内部分层）**
- **采集层** `app/ingestion`：爬虫（各源一个适配器）+ 众包提交 + Celery Beat 调度
- **解析层** `app/parsing`：公告原文 → 结构化岗位字段（规则 + LLM 抽取）
- **分析层** `app/analysis`：DeepSeek 按特征清单分析 → 疑似分 + 命中特征 + 理由 + 高亮
- **API 层** `app/api`：搜索筛选、详情+报告、众包提交、申诉
- **前端** `frontend/`：Vue3 响应式

**数据流**：`爬虫/众包 → announcements(原文) → 解析 → positions(结构化) → 分析 → analyses(报告) → 前端`，各环节 Celery + Redis 异步链式触发、失败重试。

## 5. 萝卜岗判定特征体系（产品核心）

以下四类维度作为 prompt 的分析框架，也作为 `hit_features` 的取值字典：

- **A 条件过度具体化（指向唯一性）**：专业过窄、院校学历罕见叠加、年龄异常精确、经历高度特定、证书资格刁钻、奖项荣誉论文
- **B 限制性条件（无正当理由缩小范围）**：性别/政治面貌/户籍限定、定向专项措辞
- **C 结构性信号**：名额极少却堆叠限制、组合后符合人数极少
- **D 程序性信号（辅助）**：报名窗口极短、发布隐蔽

判定取向：**以特征清单为主框架引导 DeepSeek 逐项打分**（可解释性强、结果稳定）。

## 6. 数据模型（PostgreSQL）

- **announcements**：`id, source_type(submit/crawl), source_url, raw_text, org_name, region, fetched_at, content_hash`
- **positions**：`id, announcement_id(FK), org_name, position_name, major_req, age_req, education_req, experience_req, cert_req, headcount, raw_conditions(JSONB)`
- **analyses**：`id, position_id(FK), suspicion_score(0-100), level(low/mid/high), hit_features(JSONB), reasoning(text), highlights(JSONB), model_version, analyzed_at`

Alembic 管理迁移。

## 7. 阶段 1 规格（核心分析引擎）

**范围**：仅"粘贴一份招聘公告文本 → 输出疑似度分析报告"端到端闭环 + 报告落库 + 基础 Web 页面。不含爬虫/众包采集，但数据模型预留字段。暂不引入 Celery（单次分析同步即可）。

**分析引擎**：
- DeepSeek 用 OpenAI 兼容 SDK（`base_url=https://api.deepseek.com`），key 从环境变量读
- prompt = System（萝卜岗定义 + 判定原则，强调客观/给依据/用"疑似"措辞）+ 注入特征清单 + 1-2 个 few-shot
- 严格 JSON 输出：`{ suspicion_score, level, hit_features:[{key, evidence, quote}], reasoning, highlights:[{text, reason}] }`
- engine 做 JSON 校验/重试、评分归一化、分级映射（默认 0-39 低 / 40-69 中 / 70-100 高，阈值可配）

**API**：
- `POST /api/analyze` `{ text }` → `extractor → engine → 落库` → `{ position, analysis }`
- `GET /api/analyses/{id}` → 报告详情

**前端**：单页——粘贴框 → 提交 → 疑似度仪表盘 + 命中特征卡片 + 高亮原文 + 固定免责声明。

## 8. 合规与风险处理（生命线）

- 爬虫遵守 robots、限频、只抓公开招聘信息、保留原文出处链接
- 全站"AI 疑似推测，仅供参考，不构成结论"免责声明，杜绝绝对化定性
- 提供单位/个人**纠错与下架申诉入口**；不推断、不展示具体个人隐私
- 数据境内存储；定位"促进招聘公开透明"的中性公益工具

## 9. 验证标准（阶段 1）

1. **金标准回归测试**：5-10 个样本（已知萝卜岗 + 正常岗），断言萝卜岗得高分、正常岗得低分（容忍区间）
2. **特征体系单测**：特征字典完整性、`hit_features` key 合法性
3. **手动端到端**：起 PG → 配 `DEEPSEEK_API_KEY` → 起后端 + 前端 → 贴已知萝卜岗公告，确认高分 + 可疑条件正确高亮 + 理由合理；再贴正常岗确认低分
4. **API 冒烟**：`POST /api/analyze` 返回结构符合 schema

## 10. 分阶段路线

1. **阶段 1 核心引擎**（本规格）：数据模型 + 分析引擎 + 粘贴分析单页 + 基础 Web
2. **阶段 2 区域贯通**：1-2 个数据源爬虫 + 解析 + 入库 + 搜索浏览（引入 Celery+Redis）
3. **阶段 3 全国铺量**：扩展数据源 + 众包入口 + 申诉机制 + 运营后台
4. **阶段 4 规模化**：金标准评测体系 + 模型调优 + 性能扩展

## 11. 待用户提供 / 确认

- **DeepSeek API Key**（DeepSeek 开放平台注册）
- **金标准样本**：真实萝卜岗/正常岗案例 3-5 个（无则先构造）
- **前端框架**：默认 Vue3 + Vite，可改 React
