# paper-quick-reader

AI 论文速读：三档深度（裸读 / 引导 / 精读）+ 页码级 Provenance 防幻觉 + 多篇对比。

## 安装

只要这一个 skill —— 稀疏克隆，只拉取本目录：

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/lzptouch/agent-skills.git
cd agent-skills
git sparse-checkout set papers/paper-quick-reader
ln -s "$PWD/papers/paper-quick-reader" ~/.codebuddy/skills/paper-quick-reader
```

已经整仓克隆过时，在仓库根目录执行：

```bash
./scripts/install.sh paper-quick-reader            # 软链（git pull 即升级）
./scripts/install.sh --copy paper-quick-reader     # 复制，Windows 或要改本地副本时用
```

不想用 git，就下载 [Releases](https://github.com/lzptouch/agent-skills/releases/latest) 里的 `paper-quick-reader.zip`，解压到 `~/.codebuddy/skills/`。

要锁在某个版本（不改动工作区，装完打印实际版本）：

```bash
./scripts/install.sh --ref paper-quick-reader-v<version> paper-quick-reader
```

## 依赖

```bash
pip install pdfplumber pymupdf python-docx   # PDF / DOCX 解析
pip install weasyprint                        # 可选：PDF 报告渲染，缺失则降级 HTML
```

纯 `pasted_text` 输入时不需要任何第三方库。

## 用法

直接说要读什么即可，典型表述：读一下这篇论文 / 抓核心观点 / 对比这三篇 / 第几页提到 X / 这篇的数据集怎么构造的 / 论文精读。

**不做**：论文检索、文献管理、论文翻译、扫描件 OCR、论文写作与降重。

## 结构

| 目录 | 内容 |
|---|---|
| `SKILL.md` | 主流程：9 步工作流、输入/输出契约、NEVER 禁令 |
| `references/` | 判定路由、质量 rubric、provenance 规则、异常映射表等 18 篇 |
| `scripts/` | `parse_pdf.py` / `fetch_arxiv_tex.py` / `verify_provenance.py` / `render_report.py` / `calibrate.py` |
| `assets/` | HTML 报告模板 |

详见 [SKILL.md](SKILL.md)。
