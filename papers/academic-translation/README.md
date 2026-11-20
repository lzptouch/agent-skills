# academic-translation

学术论文翻译与润色：直译 → 反思 → 雅化三步法，公式/引用零损伤，支持双栏对照输出。

## 安装

只要这一个 skill —— 稀疏克隆，只拉取本目录：

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/lzptouch/agent-skills.git
cd agent-skills
git sparse-checkout set papers/academic-translation
ln -s "$PWD/papers/academic-translation" ~/.codebuddy/skills/academic-translation
```

已经整仓克隆过时，在仓库根目录执行：

```bash
./scripts/install.sh academic-translation            # 软链（git pull 即升级）
./scripts/install.sh --copy academic-translation     # 复制，Windows 或要改本地副本时用
```

不想用 git，就下载 [Releases](https://github.com/lzptouch/agent-skills/releases/latest) 里的 `academic-translation.zip`，解压到 `~/.codebuddy/skills/`。

要锁在某个版本（不改动工作区，装完打印实际版本）：

```bash
./scripts/install.sh --ref academic-translation-v<version> academic-translation
```

## 依赖

```bash
pip install pdfplumber   # PDF 文本与公式抽取
# curl 用于 arXiv 抓取（系统自带）
```

## 用法

典型表述：把这篇论文翻译成英文 / 润色成顶会风格 / 改掉 Chinglish / 生成中英双栏对照 / 保留 LaTeX 公式翻译。

用户术语表：复制 `config/user-glossary.template.yaml` 为 `config/user-glossary.yaml` 后填写，翻译时会被优先采用。

## 结构

| 目录 | 内容 |
|---|---|
| `SKILL.md` | 输入路由、三步翻译流程、质量自检 |
| `references/` | 三步法细则、学术润色、Chinglish 模式、公式保护、选词表、分领域术语库（`glossary/`） |
| `scripts/` | `extract_pdf.py` 抽取、`preserve_latex.py` 公式保护、`arxiv_fetch.sh` 抓取 |
| `assets/templates/` | Markdown / LaTeX / HTML 双栏对照模板、自检报告模板 |
| `config/` | 用户术语库模板 |

详见 [SKILL.md](SKILL.md)。
