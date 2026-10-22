# Linguistics PhD Program Explorer — 计划

> 由 Communication PhD Program Explorer（`Junyu-Jiang0508/communication_phd`）改造而来。站点代码、匹配算法、数据管线沿用；
> 原站的拆解、匹配评测和技术决定见 Communication 仓库的 `docs/PLAN.md`。本文只记录语言学版本的不同之处。

## 0. 一句话目标

给准备申请美国语言学 PhD 的人一个"先写研究兴趣、再找导师与项目"的工具，覆盖语言学系本身，
也覆盖语言学申请者常常同样适合的相关院系：计算语言学/NLP、应用语言学/二语习得、语种系里的语言学、言语听力与认知科学。

## 1. 决定（2026-10-22）

- **新仓库**：`linguistics_phd`，独立的 GitHub Pages 地址；Communication 站点保持不变。
- **项目范围**：美国所有授予语言学研究型 PhD 的大学（以 LSA 目录为起点，逐校在官网核实），外加四类相关院系。
- **院系类型（field）**：每个院系、每位教师都标注 `LING / COMP / APPLIED / LANG / SPEECH`，匹配页与名录页都可以按类型筛选；
  项目页上每个院系带类型标签。相关院系只收录研究语言的教师（例如 CS 系只收 NLP 方向，语种系只收语言学家），规则见 `pipeline/WORKFLOWS.md`。
- **标签体系**：沿用五个维度的代码键（topic / approach / data / setting / region），含义改为
  研究领域 21 / 方法 14 / 数据 12 / 人群与场景 11 / 语言与地区 14。保留键名意味着前端、校验脚本、配色不用改。
- **"地区"维度改为"语言"**：语言学里"研究哪种语言"比"在哪个地区"重要得多，提示加权也最高（0.25）。
- **提示规则**移到 `pipeline/hints.json`，浏览器（match.ts）和评测脚本（harness.py）读同一份文件，避免两边不同步。
- **站点信息**（名称、作者、仓库、联系邮箱）集中在 `src/lib/site.ts`。
- **不展示排名**，与 Communication 站点一致。
- **视觉**：暂时沿用 Communication 的"测试卡彩条"设计，作为姊妹站；是否为语言学另做视觉签名待定。

## 2. 数据管线

```
data/programs_seed.json（65 所候选：56 所预期有语言学系 PhD，另有只含相关院系的学校）
        │  Workflow 1 discover：逐校核实 PhD、院系、类型、名录 URL
        ▼
data/programs_discovered.json → 人工复核 → data/programs.json
        │  Workflow 2 scrape → data/raw/<slug>.json（每人带 unit，决定其 field）
        │  Workflow 3 label  → data/labels/<slug>.json
        ▼
pipeline/build.py → src/data/*.json + public/search/*
```

三个 workflow 的完整说明写在 `pipeline/WORKFLOWS.md`（Communication 版本当时没有把这些提示词提交进仓库）。

## 3. 需要重新做的部分

| 部分 | 状态 |
|---|---|
| 站点代码、文案、中英文界面 | 已改为语言学 |
| 标签体系、提示规则、中文术语表 | 已写，待真实数据检验 |
| 校准用 probes（32 条） | 已写 |
| 评测查询（40 条：30 段落 / 6 关键词 / 4 中文） | 已写，未打分 |
| 项目名单 | 种子已写，待 discover |
| 抓取、打标签、构建向量 | 待在本机运行 |
| 匹配评测（nDCG@10） | 待数据完成后做；可能需要提高关键词权重 |

## 4. 风险

| 风险 | 对策 |
|---|---|
| 相关院系把大量与语言无关的教师带进来（CS、言语听力） | WORKFLOWS.md 的收录规则只收语言方向教师；界面可按院系类型筛选 |
| 同一人在语言学系和相关院系重复出现 | 每所大学内按姓名去重，记在主聘院系 |
| 语言名、术语在嵌入向量里信号弱 | 关键词（BM25）与"语言"维度提示加权；评测后再调权重 |
| 部分学校的语言学 PhD 已停招或只有硕士 | discover 步骤逐校核实，`include:false` 并写明原因 |
