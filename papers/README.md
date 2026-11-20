# papers — 论文场景

本分类下的 skill 围绕「找论文 / 读论文 / 翻论文」。3 个 skill 彼此独立，可以只装一个，也可以整分类装齐。

| Skill | 一句话 | 典型触发 | 依赖 |
|---|---|---|---|
| [paper-quick-reader](paper-quick-reader/) | 三档深度速读（裸读 / 引导 / 精读）+ 页码级 provenance 防幻觉 + 多篇对比 | 「读一下这篇论文」「抓核心观点」「对比这三篇」 | python3；可选 `pdfplumber` `pymupdf` `weasyprint` |
| [academic-translation](academic-translation/) | 直译 → 反思 → 雅化三步学术翻译，公式零损伤，双栏对照 | 「把这篇翻成英文」「润色成顶会风格」「改掉 Chinglish」 | python3 + `pdfplumber`；`curl` |
| [arxiv-watcher](arxiv-watcher/) | 按关键词 / 作者 / 分类检索 arXiv，摘要并归档 | 「arXiv 上关于 X 的最新工作」「今天有什么新论文」 | `curl` |

## 怎么选

| 你要做的事 | 装这个 |
|---|---|
| 快速读懂一篇 PDF、抓核心贡献、多篇横向对比 | `paper-quick-reader` |
| 中英互译、润色成顶会风格、去 Chinglish | `academic-translation` |
| 追踪某个关键词 / 作者 / 分类的新论文 | `arxiv-watcher` |

常见组合：

- **跟新 + 精读**：`arxiv-watcher` 筛出候选，`paper-quick-reader` 精读里面对口的几篇。
- **精读 + 输出英文**：`paper-quick-reader` 提炼，`academic-translation` 转写成英文稿。

## 安装

客户端**只识别一层目录**，所以要装的是 `papers/<skill>/` 这个目录，而不是 `papers/`：

```bash
git clone https://github.com/lzptouch/agent-skills.git
cd agent-skills
./scripts/install.sh                       # 全部 3 个
./scripts/install.sh paper-quick-reader    # 只装一个
```

只要一个 skill（稀疏克隆）、不想用 git（下 zip）、锁定到某个版本、升级/卸载：看仓库根 [README](../README.md)，以及维护者本地笔记 `doc/02-用户-安装与使用.md`（`doc/` 已写入 `.gitignore`，不随仓库分发）。

## 目录

```text
papers/
├── README.md               # 本文件：分类入口
├── paper-quick-reader/     # SKILL.md + scripts/ + references/ + assets/
├── academic-translation/
└── arxiv-watcher/
```

每个 skill 的具体能力边界、不适用场景、依赖安装与产物位置，写在它自己的 `README.md` 和 `SKILL.md` 里。

## 往本分类加 skill

在 `papers/` 下新建 `<skill>/SKILL.md`（`name` 与目录同名、`version` 必填），跑 `python3 scripts/validate.py`，然后在本页的两张表里各补一行。流程与校验项见本地 `doc/03-仓库结构与开发发布参考.md`。

⚠️ skill 名全仓库唯一：`papers/` 下已用掉 `paper-quick-reader`、`academic-translation`、`arxiv-watcher`，未来在其它分类里也不能重名。
