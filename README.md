# Agent Skills 合集

按分类组织的 Agent Skills 仓库。每个 skill 都是自包含目录（`SKILL.md` + 可选 `scripts/` `references/` `assets/`），彼此不依赖：**可以整仓克隆一次装齐全，也可以只把其中一个 skill 拉下来用**。适配任何遵循 `SKILL.md` 规范的客户端（CodeBuddy、Claude Code 及其它 Agent Skills 运行时）。

## 分类

| 分类 | 内容 | 入口 |
|---|---|---|
| `papers/` | 论文速读、学术翻译、arXiv 追踪（3 个 skill） | [papers/README.md](papers/README.md) |

新增分类（如 `coding/`、`writing/`）时在本表加一行，并给该目录写一份 README 作为分类入口。

## 目录约定

```text
<category>/<skill>/SKILL.md     # 一个 skill
```

- **分类层只做归类**，本身不是 skill（不含 `SKILL.md`）。
- **skill 名全局唯一**：不同分类下不能同名（否则 zip 与安装目录会互相覆盖）。
- **对外发布的东西以 skill 名命名**：tag、zip、Release 附件、安装目录都只用 `name`，不带分类前缀。
- 仓库根下 `scripts/`、`doc/`、`dist/`、`.github/` 是设施，不参与 skill 发现。

## 安装

客户端**只识别一层目录**（不会递归扫描），所以安装 = 把**包含 `SKILL.md` 的那个目录**放进 skills 目录：

| 客户端 | 用户级（所有项目） | 项目级 |
|---|---|---|
| CodeBuddy | `~/.codebuddy/skills/` | `<项目>/.codebuddy/skills/` |
| Claude Code | `~/.claude/skills/` | `<项目>/.claude/skills/` |

克隆整个仓库后**不能**直接把仓库目录（或 `papers/` 分类目录）丢进 skills 目录，要用仓库自带的 `scripts/install.sh` 把每个 skill 分别挂进去：

```bash
git clone https://github.com/lzptouch/agent-skills.git
cd agent-skills
./scripts/install.sh          # 软链仓库内全部 skill，之后 git pull 即升级
```

| 命令 | 作用 |
|---|---|
| `./scripts/install.sh` | 软链全部 skill |
| `./scripts/install.sh paper-quick-reader arxiv-watcher` | 只挂指定的几个 |
| `./scripts/install.sh --copy` | 复制而非软链（Windows、或要改本地副本） |
| `./scripts/install.sh -t ./.codebuddy/skills` | 装到项目级目录 |
| `./scripts/install.sh -f` | 覆盖已存在的同名目录 |
| `./scripts/install.sh -l` | 列出仓库内所有 skill |

安装后重启客户端，skill 的 `name` 会出现在技能列表里。

只要一个 skill（稀疏克隆）、不用 git（下 zip）、锁定到某个版本、升级与卸载：见 [papers/README.md](papers/README.md) 与维护者本地笔记 `doc/02-用户-安装与使用.md`（`doc/` 已写入 `.gitignore`，不随仓库分发）。

## 许可

本仓库整体采用 [MIT License](LICENSE)。
