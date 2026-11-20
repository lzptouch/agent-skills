#!/usr/bin/env python3
"""校验本仓库内所有 skill 是否符合 Skill 格式规范。

仓库布局：``<category>/<skill>/SKILL.md``（如 papers/paper-quick-reader）。
``find_skills`` 同时兼容 ``<skill>/SKILL.md`` 的平铺布局。

用法：
    python3 scripts/validate.py            # 校验全部
    python3 scripts/validate.py <dir>      # 只校验某个 skill 目录

检查项：
  E1  SKILL.md 存在（每个 skill 目录必须且只能有一个）
  E2  YAML frontmatter 以 --- 开头并有结束 ---
  E3  name 必填、hyphen-case、与目录名一致
  E4  description 必填、不含 < >、长度 >= 20
  E5  Markdown 文档互链（*.md）与 scripts/ 下的文件必须真实存在
  E6  version 必填且为 semver（x.y.z）—— 发布 tag 与 zip 命名依赖它
  W1  出现 scripts/ references/ assets/ config/ 之外的顶层目录
  W2  scripts/ 下的文件缺少可执行权限（.sh）

不依赖任何第三方包。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOWED_DIRS = {"scripts", "references", "assets", "config"}
# 仓库根下这些目录是设施/产物，不当作分类目录扫描
RESERVED_DIRS = {"scripts", "doc", "dist", "node_modules"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\s*(\r?\n|$)", re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)")
# 运行期产物 / 占位符，不参与存在性校验
SKIP_TOKENS = (
    "{", "}", "<", ">", "://", "#", "url1", "url2", "YYMM",
    "result.json", "provenance-audit.json", "comparison.table", "_skill_meta.json",
)


def _frontmatter(text: str) -> str | None:
    m = FM_RE.match(text)
    return m.group(1) if m else None


def _field(fm: str, key: str) -> str | None:
    m = re.search(rf"^{key}:\s*(.+)$", fm, re.MULTILINE)
    if not m:
        return None
    value = m.group(1).strip()
    return value[1:-1] if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'" else value


def read_version(skill_dir: Path) -> str | None:
    """读取 SKILL.md frontmatter 的 version；供 build_packages / verify_tag 复用。"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return None
    fm = _frontmatter(skill_md.read_text(encoding="utf-8"))
    return _field(fm, "version") if fm else None


def check_skill(skill_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []
    name = skill_dir.name

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"E1 缺少 SKILL.md"], warns

    text = skill_md.read_text(encoding="utf-8")
    fm = _frontmatter(text)
    if fm is None:
        return ["E2 frontmatter 缺失或未以 --- 包裹"], warns

    got_name = _field(fm, "name")
    if not got_name:
        errors.append("E3 frontmatter 缺少 name")
    else:
        if not NAME_RE.match(got_name):
            errors.append(f"E3 name '{got_name}' 非 hyphen-case")
        if got_name != name:
            errors.append(f"E3 name '{got_name}' 与目录名 '{name}' 不一致")

    desc = _field(fm, "description")
    if not desc:
        errors.append("E4 frontmatter 缺少 description（或使用了 YAML 折叠/块标量，请写成单行）")
    else:
        if "<" in desc or ">" in desc:
            errors.append("E4 description 含尖括号 < >")
        if len(desc) < 20:
            errors.append(f"E4 description 过短（{len(desc)} 字符），需说明用途与触发条件")

    ver = _field(fm, "version")
    if not ver:
        errors.append("E6 frontmatter 缺少 version（形如 1.0.0；发布 tag 与 zip 命名依赖它）")
    elif not SEMVER_RE.match(ver):
        errors.append(f"E6 version '{ver}' 非 semver（应为 x.y.z）")

    for d in sorted(p for p in skill_dir.iterdir() if p.is_dir()):
        if d.name not in ALLOWED_DIRS and not d.name.startswith("."):
            warns.append(f"W1 非标准顶层目录: {d.name}/（规范仅 scripts/ references/ assets/）")

    for f in skill_dir.rglob("*"):
        if not f.is_file() or ".git" in f.parts:
            continue
        if f.suffix == ".sh" and not (f.stat().st_mode & 0o111):
            warns.append(f"W2 脚本无可执行权限: {f.relative_to(skill_dir)}")

        # assets/ 下是产出模板，允许包含指向运行期产物的示例链接
        if f.suffix != ".md" or "assets" in f.relative_to(skill_dir).parts:
            continue
        for target in LINK_RE.findall(f.read_text(encoding="utf-8")):
            if any(tok in target for tok in SKIP_TOKENS):
                continue
            if target.startswith(("http", "mailto")):
                continue
            if f.suffix != ".md":
                continue
            rel = target.split("#")[0]
            if not rel:
                continue
            authored = rel.endswith(".md") or rel.startswith(("scripts/", "./scripts/"))
            if not authored:
                continue
            base = (f.parent / rel).resolve()
            root_base = (skill_dir / rel).resolve()
            if not (base.exists() or root_base.exists()):
                errors.append(f"E5 断链: {f.relative_to(skill_dir)} -> {rel}")
    return errors, warns


def find_skills(root: Path) -> list[Path]:
    """发现 skill 目录：优先 ``<category>/<skill>/SKILL.md``，也接受 ``<skill>/SKILL.md``。"""
    found: list[Path] = []
    for top in sorted(root.iterdir()):
        if not top.is_dir() or top.name.startswith(".") or top.name in RESERVED_DIRS:
            continue
        if (top / "SKILL.md").is_file():
            found.append(top)
            continue
        for sub in sorted(top.iterdir()):
            if sub.is_dir() and not sub.name.startswith(".") and (sub / "SKILL.md").is_file():
                found.append(sub)
    return found


def duplicate_names(skills: list[Path], root: Path) -> dict[str, list[Path]]:
    """同名 skill 会让 zip / 安装目录互相覆盖，必须视为错误。"""
    groups: dict[str, list[Path]] = {}
    for sk in skills:
        groups.setdefault(sk.name, []).append(sk)
    return {n: ps for n, ps in groups.items() if len(ps) > 1}


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    if len(sys.argv) > 1:
        skills = [Path(sys.argv[1]).resolve()]
    else:
        skills = find_skills(root)

    if not skills:
        print("未找到任何 skill 目录（期望 <category>/<skill>/SKILL.md）")
        return 1

    dup = duplicate_names(skills, root)
    if dup:
        for name, paths in dup.items():
            where = ", ".join(str(p.relative_to(root)) for p in paths)
            print(f"错误: skill 名重复 '{name}': {where}（不同分类下不能同名）")
        return 1

    total_err = 0
    total_warn = 0
    for sk in skills:
        errors, warns = check_skill(sk)
        status = "PASS" if not errors else "FAIL"
        try:
            label = f"{sk.name}  ({sk.relative_to(root).as_posix()})"
        except ValueError:
            label = sk.name
        print(f"[{status}] {label}  ({len(errors)} error, {len(warns)} warning)")
        for e in errors:
            print(f"        ERROR  {e}")
        for w in warns:
            print(f"        WARN   {w}")
        total_err += len(errors)
        total_warn += len(warns)

    print(f"\n汇总: {len(skills)} 个 skill · {total_err} error · {total_warn} warning")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
