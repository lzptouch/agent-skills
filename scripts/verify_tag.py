#!/usr/bin/env python3
"""校验发布 tag 与 SKILL.md frontmatter 的 version 是否一致。

支持两种 tag：
    v1.2.0                      整仓快照（所有 skill 一起发）
    paper-quick-reader-v1.2.0  单 skill 发布（只需该 skill 的 version 对得上）

用法：
    python3 scripts/verify_tag.py                       # 读 GITHUB_REF_NAME / 当前 HEAD 的 tag
    python3 scripts/verify_tag.py paper-quick-reader-v1.2.0
    python3 scripts/verify_tag.py <tag> --github-output  # 输出 skills=... 供 CI 消费

不一致时退出码 1 —— 防止「改了代码忘了改版本号」发出一个语义错误的 release。
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import SEMVER_RE, duplicate_names, find_skills, read_version  # noqa: E402

SINGLE_RE = re.compile(r"^(?P<name>.+)-v(?P<ver>\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)$")
REPO_RE = re.compile(r"^v(?P<ver>\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)$")


def current_tag() -> str:
    env = os.environ.get("GITHUB_REF_NAME")
    if env:
        return env
    try:
        out = subprocess.run(
            ["git", "describe", "--tags", "--exact-match", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    github_output = "--github-output" in sys.argv
    root = Path(__file__).resolve().parent.parent

    tag = args[0] if args else current_tag()
    if not tag:
        print("错误: 没有指定 tag，且当前 HEAD 不是 tag（或不在 git 仓库）", file=sys.stderr)
        return 1

    skills = find_skills(root)
    dup = duplicate_names(skills, root)
    if dup:
        for name, paths in dup.items():
            where = ", ".join(str(p.relative_to(root)) for p in paths)
            print(f"错误: skill 名重复 '{name}': {where}", file=sys.stderr)
        return 1
    by_name = {s.name: s for s in skills}

    m = SINGLE_RE.match(tag)
    if m and m.group("name") in by_name:
        name, want = m.group("name"), m.group("ver")
        got = read_version(by_name[name])
        if got != want:
            print(
                f"错误: tag '{tag}' 声明 {want}，但 {name}/SKILL.md 里是 version: {got or '(缺失)'}\n"
                f"      先改 frontmatter version 再打 tag，或修正 tag 名",
                file=sys.stderr,
            )
            return 1
        selected = [name]
        print(f"[PASS] {tag} -> {name} v{got}")
    elif REPO_RE.match(tag):
        print(f"[PASS] {tag} -> 整仓快照（{len(skills)} 个 skill）")
        selected = [s.name for s in skills]
    else:
        avail = ", ".join(f"{n}-v{read_version(s)}" for n, s in sorted(by_name.items()))
        print(
            f"错误: tag '{tag}' 不符合发布约定\n"
            f"      整仓: v1.2.0    单 skill: <skill>-v1.2.0\n"
            f"      当前可发布: {avail}",
            file=sys.stderr,
        )
        return 1

    if github_output:
        print(f"skills={' '.join(selected)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
