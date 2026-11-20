# 样例与自测索引

> 端到端样例（`result.json` / `provenance-audit.json` / HTML 报告 / 原始 PDF）**不随本 skill 分发**：
> 原始 PDF 体积过大，会挤占 references 的上下文预算。需要时按下面的方法自行生成。

## 样例矩阵（自行生成）

| 样例 | 模式 | 覆盖点 |
|---|---|---|
| `single-skim-selfinstruct` | single + skim | 单篇裸读最小路径 |
| `single-deep-dive-selfinstruct` | single + deep | 单篇精读 + provenance 审计 |
| `compare-3papers-alignment` | compare × 3 篇 | 多篇对比（Self-Instruct / Alpaca / LIMA） |

## 如何生成

1. 取任一可公开下载的 arXiv PDF，按 SKILL.md 第 1 步解析出 `paper_text`。
2. 按目标模式跑完整流程，产物落在 `paper-reader-output/{slug}/`：
   - `result.json` —— 结构化结果（黄金样本）
   - `provenance-audit.json` —— 引文核对结果
   - `report.html` / `report.md` —— 渲染产物
3. 用 `scripts/verify_provenance.py` 复核，期望 0 条 `UNVERIFIED`。

## LLM 使用建议

- **读 schema** → 读 [output-schema.md](output-schema.md)，不需要真实 `result.json`
- **写 few-shot** → 用 [calibration/](calibration/) 里的锚点，已随 skill 内置
- **debug 渲染** → 对 `paper-reader-output/*/result.json` 直接跑 `scripts/render_report.py`
