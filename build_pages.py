#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

UPSTREAM_VCSKY = "https://cdn.dos.zone/vcsky/"
UPSTREAM_VCBR = "https://br.cdn.dos.zone/vcsky/"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label} match, found {count}. Upstream may have changed.")
    return text.replace(old, new, 1)


def build(upstream: Path, output: Path, wrapper: Path) -> None:
    dist = upstream / "dist"
    if not dist.is_dir():
        raise RuntimeError(f"Upstream dist/ directory not found: {dist}")

    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(dist, output)

    game_path = output / "game.js"
    index_path = output / "index.html"
    if not game_path.exists() or not index_path.exists():
        raise RuntimeError("Expected dist/game.js and dist/index.html in upstream repository")

    game = game_path.read_text(encoding="utf-8")
    old_block = (
        '// Base URLs\n'
        'const replaceFetch = (str) => str.replace("https://cdn.dos.zone/vcsky/", "/vcsky/")\n'
        'const replaceBR = "/vcbr/"'
    )
    new_block = f'''// Base URLs - GitHub Pages adapter\nconst pagesConfig = window.REVCDOS_PAGES_CONFIG || {{}};\nconst pagesVcskyBase = pagesConfig.vcskyBaseUrl || "{UPSTREAM_VCSKY}";\nconst pagesVcbrBase = pagesConfig.vcbrBaseUrl || "{UPSTREAM_VCBR}";\nconst replaceFetch = (str) => str.replace("{UPSTREAM_VCSKY}", pagesVcskyBase)\nconst replaceBR = pagesVcbrBase'''
    game = replace_once(game, old_block, new_block, "game.js base URL block")
    game_path.write_text(game, encoding="utf-8", newline="\n")

    index = index_path.read_text(encoding="utf-8")

    if 'src="/intro.mp4"' in index:
        index = index.replace('src="/intro.mp4"', 'src="intro.mp4"', 1)

    head_marker = "<head>"
    injection = (
        '<head>\n'
        '    <script src="coi-serviceworker.js"></script>\n'
        '    <script src="pages-config.js"></script>'
    )
    index = replace_once(index, head_marker, injection, "index.html <head>")

    local_save_test = 'if (new URLSearchParams(window.location.search).get("custom_saves") === "1") {'
    if local_save_test in index:
        index = index.replace(local_save_test, 'if (false) { // local server saves are unavailable on GitHub Pages', 1)

    index_path.write_text(index, encoding="utf-8", newline="\n")

    shutil.copy2(wrapper / "pages-config.js", output / "pages-config.js")
    shutil.copy2(wrapper / "coi-serviceworker.js", output / "coi-serviceworker.js")
    (output / ".nojekyll").write_text("", encoding="utf-8")

    built_game = game_path.read_text(encoding="utf-8")
    built_index = index_path.read_text(encoding="utf-8")
    checks = {
        "config injected": "REVCDOS_PAGES_CONFIG" in built_game,
        "vcbr is configurable": "pagesVcbrBase" in built_game,
        "root intro path removed": 'src="/intro.mp4"' not in built_index,
        "COI worker included": 'src="coi-serviceworker.js"' in built_index,
        "Pages config included": 'src="pages-config.js"' in built_index,
        "nojekyll exists": (output / ".nojekyll").exists(),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError("Build validation failed: " + ", ".join(failed))

    print(f"Built GitHub Pages site at: {output}")
    for name in checks:
        print(f"  OK: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build reVCDOS for GitHub Pages")
    parser.add_argument("upstream", type=Path, help="Path to cloned Lolendor/reVCDOS repository")
    parser.add_argument("output", type=Path, nargs="?", default=Path("public"), help="Output directory")
    args = parser.parse_args()
    build(args.upstream.resolve(), args.output.resolve(), Path(__file__).resolve().parent)


if __name__ == "__main__":
    main()
