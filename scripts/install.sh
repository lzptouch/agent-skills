#!/usr/bin/env bash
# 把本仓库的 skill 挂进客户端 skills 目录。
#
#   ./scripts/install.sh                          # 软链全部 skill 到 ~/.codebuddy/skills/
#   ./scripts/install.sh paper-quick-reader       # 只装一个
#   ./scripts/install.sh --copy                   # 复制而不是软链
#   ./scripts/install.sh -t ./.codebuddy/skills   # 装到项目级目录
#   ./scripts/install.sh --ref paper-quick-reader-v1.0.0 paper-quick-reader   # 装固定版本
#   ./scripts/install.sh -l                       # 列出仓库里有哪些 skill

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${SKILLS_DIR:-$HOME/.codebuddy/skills}"
MODE="link"
FORCE=0
LIST_ONLY=0
REF=""
NAMES=()

usage() {
  cat <<'EOF'
用法: ./scripts/install.sh [选项] [skill ...]

  (无 skill 参数)     安装仓库内全部 skill
  选项:
    --link            软链（默认）。git pull 后立即生效
    --copy            复制。适合 Windows、或需要改动本地副本的场景
    -t, --target DIR  安装目标目录，默认 $SKILLS_DIR 或 ~/.codebuddy/skills
    -r, --ref REF     从 git 的指定 tag / commit 取文件（隐含 --copy）
                      例: --ref paper-quick-reader-v1.0.0
    -f, --force       目标已存在时强制覆盖（会删除同名目录）
    -l, --list        只列出仓库内的 skill，不安装
    -h, --help        显示本帮助

示例:
  ./scripts/install.sh
  ./scripts/install.sh paper-quick-reader arxiv-watcher
  ./scripts/install.sh --copy -t ./.codebuddy/skills
  ./scripts/install.sh --ref paper-quick-reader-v1.0.0 paper-quick-reader
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --link) MODE="link" ;;
    --copy) MODE="copy" ;;
    -t|--target) TARGET="${2:?--target 需要目录参数}"; shift ;;
    --target=*) TARGET="${1#*=}" ;;
    -r|--ref) REF="${2:?--ref 需要 tag 或 commit}"; shift ;;
    --ref=*) REF="${1#*=}" ;;
    -f|--force) FORCE=1 ;;
    -l|--list) LIST_ONLY=1 ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "未知参数: $1" >&2; usage >&2; exit 1 ;;
    *) NAMES+=("$1") ;;
  esac
  shift
done

# 仓库内的 skill = <category>/<skill>/SKILL.md（同时兼容一级目录 <skill>/SKILL.md）
# ALL 存 skill 名（= 安装后的目录名），RELS 存它在仓库内的相对路径（两数组按下标平行）
ALL=()
RELS=()

add_skill() {
  local dir="$1" name rel i=0 s
  name="$(basename "$dir")"
  rel="${dir#"$REPO_ROOT"/}"
  while [ "$i" -lt ${#ALL[@]} ]; do
    s="${ALL[$i]}"
    if [ "$s" = "$name" ]; then
      echo "错误: skill 名重复 '${name}'：${RELS[$i]} 与 ${rel} —— 不同分类下不能同名" >&2
      exit 1
    fi
    i=$((i + 1))
  done
  ALL+=("$name")
  RELS+=("$rel")
}

for top in "$REPO_ROOT"/*/; do
  [ -d "$top" ] || continue
  case "$(basename "$top")" in
    scripts|doc|dist|node_modules|.*) continue ;;
  esac
  if [ -f "${top}SKILL.md" ]; then
    add_skill "${top%/}"
  else
    for sub in "$top"*/; do
      [ -f "${sub}SKILL.md" ] && add_skill "${sub%/}"
    done
  fi
done

rel_of() {
  local i=0 n
  for n in "${ALL[@]}"; do
    if [ "$n" = "$1" ]; then
      printf '%s' "${RELS[$i]}"
      return 0
    fi
    i=$((i + 1))
  done
  return 1
}

if [ ${#ALL[@]} -eq 0 ]; then
  echo "仓库里没找到任何 skill（期望 <category>/<skill>/SKILL.md）" >&2
  exit 1
fi

if [ "$LIST_ONLY" -eq 1 ]; then
  printf '%s\n' "${ALL[@]}"
  exit 0
fi

if [ ${#NAMES[@]} -eq 0 ]; then
  NAMES=("${ALL[@]}")
fi

# 校验名字
for name in "${NAMES[@]}"; do
  found=0
  for s in "${ALL[@]}"; do [ "$s" = "$name" ] && found=1; done
  if [ "$found" -eq 0 ]; then
    echo "错误: 仓库里没有 skill '$name'（可用: ${ALL[*]}）" >&2
    exit 1
  fi
done

# --ref：锁定版本，只能复制（软链指向工作区，工作区不是固定版本）
if [ -n "$REF" ]; then
  MODE="copy"
  if [ ! -d "$REPO_ROOT/.git" ]; then
    echo "错误: --ref 需要 git 仓库，$REPO_ROOT 不是" >&2
    exit 1
  fi
  if ! git -C "$REPO_ROOT" rev-parse --verify --quiet "${REF}^{commit}" >/dev/null 2>&1; then
    git -C "$REPO_ROOT" fetch --quiet --tags --depth 1 origin >/dev/null 2>&1 || true
  fi
  if ! git -C "$REPO_ROOT" rev-parse --verify --quiet "${REF}^{commit}" >/dev/null 2>&1; then
    echo "错误: 找不到 ref '$REF'（先 git fetch --tags，或用 git tag -l 查看）" >&2
    exit 1
  fi
  for name in "${NAMES[@]}"; do
    rel="$(rel_of "$name")"
    if ! git -C "$REPO_ROOT" cat-file -e "${REF}:${rel}/SKILL.md" 2>/dev/null; then
      echo "错误: ref '$REF' 里没有 skill '$name'（${rel}）" >&2
      exit 1
    fi
  done
fi

mkdir -p "$TARGET"

installed=0
skipped=0
for name in "${NAMES[@]}"; do
  rel="$(rel_of "$name")"
  src="$REPO_ROOT/$rel"
  dst="$TARGET/$name"

  if [ -e "$dst" ] || [ -L "$dst" ]; then
    same=0
    # 软链已指向同一目录时幂等跳过；--ref 模式除外（要的是固定版本，不是工作区）
    if [ -z "$REF" ] && [ -L "$dst" ] \
       && [ "$(cd "$dst" && pwd -P)" = "$(cd "$src" && pwd -P)" ]; then
      same=1
    fi
    if [ "$same" -eq 1 ]; then
      echo "  已就绪  $name"
      installed=$((installed + 1))
      continue
    fi
    if [ "$FORCE" -ne 1 ]; then
      echo "  跳过    ${name}（${dst} 已存在，加 -f 覆盖）"
      skipped=$((skipped + 1))
      continue
    fi
    rm -rf "$dst"
  fi

  if [ -n "$REF" ]; then
    # 直接从 git 对象树导出，不切换工作区、不改动当前 checkout
    tmp="$(mktemp -d "${TMPDIR:-/tmp}/skill-ref.XXXXXX")"
    git -C "$REPO_ROOT" archive --format=tar "$REF" -- "$rel" | tar -x -C "$tmp"
    mv "$tmp/$rel" "$dst"
    rm -rf "$tmp"
    ver="$(awk 'NR==1&&/^---/{f=1;next} f&&/^---/{exit} f&&/^version:/{gsub(/"/,"",$2);print $2;exit}' "$dst/SKILL.md")"
    echo "  ${REF}  $name${ver:+ (v$ver)} <- ${rel}"
  elif [ "$MODE" = "link" ]; then
    ln -s "$src" "$dst"
    echo "  软链    $name -> $src"
  else
    cp -R "$src" "$dst"
    echo "  复制    $name -> $dst"
  fi
  installed=$((installed + 1))
done

echo
echo "完成: $installed 个已安装，$skipped 个跳过"
echo "目标目录: $TARGET"
if [ -n "$REF" ]; then
  echo "提示: 固定版本 ${REF}（复制模式），升级需重新执行 --ref"
elif [ "$MODE" = "link" ]; then
  echo "提示: 软链模式下 git pull 即完成升级"
fi
echo "提示: 重启客户端后 skill 才会出现在技能列表里"
