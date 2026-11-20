#!/usr/bin/env python3
"""把每个 skill 打成可单独下载的 zip。

用法：
    python3 scripts/build_packages.py                 # 输出到 dist/
    python3 scripts/build_packages.py --out ./public   # 自定义输出目录

产物（每个 skill 两份同名内容的 zip）：
    dist/<skill>-v<version>.zip   固定版本，可长期归档、被锁定
    dist/<skill>.zip              滚动别名，始终指向最新一次构建
    dist/SHA256SUMS               全部 zip 的 sha256

打包前会先跑 scripts/validate.py，校验不通过直接退出。
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import duplicate_names, find_skills, read_version  # noqa: E402

EXCLUDE_DIRS = {"__pycache__", ".git", ".pytest_cache", ".mypy_cache"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db"}
EXCLUDE_SUFFIX = {".pyc", ".pyo"}


def iter_files(skill_dir: Path):
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.name in EXCLUDE_FILES or path.suffix in EXCLUDE_SUFFIX:
            continue
        yield path


def build(skill_dir: Path, out_dir: Path, filename: str) -> Path:
    zip_path = out_dir / filename
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in iter_files(skill_dir):
            zf.write(path, path.relative_to(skill_dir.parent))
    return zip_path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(root / "dist"))
    parser.add_argument("--skip-validate", action="store_true")
    parser.add_argument(
        "--no-alias",
        action="store_true",
        help="只产出带版本号的 zip，不产出 <skill>.zip 滚动别名",
    )
    args = parser.parse_args()

    if not args.skip_validate:
        rc = subprocess.call([sys.executable, str(root / "scripts" / "validate.py")])
        if rc != 0:
            print("\n校验未通过，终止打包")
            return rc

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.zip"):
        old.unlink()

    skills = find_skills(root)
    if not skills:
        print("未找到任何 skill 目录（期望 <category>/<skill>/SKILL.md）")
        return 1
    dup = duplicate_names(skills, root)
    if dup:
        for name, paths in dup.items():
            where = ", ".join(str(p.relative_to(root)) for p in paths)
            print(f"错误: skill 名重复 '{name}': {where}（zip 与安装目录会互相覆盖）")
        return 1

    sums: list[str] = []
    print()
    for skill in skills:
        ver = read_version(skill) or "0.0.0"
        pinned = build(skill, out_dir, f"{skill.name}-v{ver}.zip")
        names = [pinned]
        if not args.no_alias:
            alias = out_dir / f"{skill.name}.zip"
            shutil.copyfile(pinned, alias)
            names.append(alias)
        files = sum(1 for _ in iter_files(skill))
        size = pinned.stat().st_size / 1024
        print(f"  {pinned.name:<40} {size:7.1f} KB  {files:3d} files")
        for path in names:
            sums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")

    (out_dir / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(f"\n输出目录: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
