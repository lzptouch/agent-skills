# arxiv-watcher

按关键词 / 作者 / 分类检索 arXiv，产出摘要清单并归档到本地调研日志。

## 安装

只要这一个 skill —— 稀疏克隆，只拉取本目录：

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/lzptouch/agent-skills.git
cd agent-skills
git sparse-checkout set papers/arxiv-watcher
ln -s "$PWD/papers/arxiv-watcher" ~/.codebuddy/skills/arxiv-watcher
```

已经整仓克隆过时，在仓库根目录执行：

```bash
./scripts/install.sh arxiv-watcher            # 软链（git pull 即升级）
./scripts/install.sh --copy arxiv-watcher     # 复制，Windows 或要改本地副本时用
```

不想用 git，就下载 [Releases](https://github.com/lzptouch/agent-skills/releases/latest) 里的 `arxiv-watcher.zip`，解压到 `~/.codebuddy/skills/`。

要锁在某个版本（不改动工作区，装完打印实际版本）：

```bash
./scripts/install.sh --ref arxiv-watcher-v<version> arxiv-watcher
```

## 依赖

仅需系统自带 `curl`（脚本直接调 arXiv API，无需 `arxiv` Python 包）。

## 用法

典型表述：arXiv 上关于 X 的最新工作 / 今天有什么新论文 / 帮我盯一下某个方向的更新。

直接调脚本：

```bash
bash scripts/search_arxiv.sh 'cat:cs.CL AND abs:"retrieval augmented generation"'
```

结果会归档到 `memory/RESEARCH_LOG.md`（相对本 skill 根目录，首次写入前需创建 `memory/`）。

## 结构

| 文件 | 内容 |
|---|---|
| `SKILL.md` | 查询语法、结果筛选与摘要规则、归档格式 |
| `scripts/search_arxiv.sh` | arXiv API 查询封装 |

详见 [SKILL.md](SKILL.md)。
