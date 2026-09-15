#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

UPSTREAM_VCSKY = "https://cdn.dos.zone/vcsky/"
UPSTREAM_VCBR = "https://br.cdn.dos.zone/vcsky/"
BUILD_VERSION = "17"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label} match, found {count}. Upstream may have changed.")
    return text.replace(old, new, 1)


def git_sha(repo: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


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

    old_fetch = "    const response = await fetch(data_content);"
    new_fetch = '''    let response;\n    try {\n        response = await fetch(data_content, { cache: "default" });\n    } catch (error) {\n        console.error("Failed to fetch game data:", data_content, error);\n        const status = document.getElementById("status");\n        if (status) {\n            status.textContent = "Não foi possível obter os dados do jogo desta origem. Use seus arquivos originais ou uma hospedagem autorizada.";\n        }\n        throw error;\n    }\n    if (!response.ok) {\n        const error = new Error(`Game data request failed: ${response.status} ${response.statusText}`);\n        console.error(error, data_content);\n        throw error;\n    }'''
    if old_fetch in game:
        game = game.replace(old_fetch, new_fetch, 1)
    game_path.write_text(game, encoding="utf-8", newline="\n")

    index = index_path.read_text(encoding="utf-8")

    replacements = {
        'src="/intro.mp4"': 'src="intro.mp4"',
        "src='/intro.mp4'": "src='intro.mp4'",
        'src="/cover.jpg"': 'src="cover.jpg"',
        "src='/cover.jpg'": "src='cover.jpg'",
        'href="/cover.jpg"': 'href="cover.jpg"',
        "href='/cover.jpg'": "href='cover.jpg'",
        "url('/cover.jpg')": "url('cover.jpg')",
        'url("/cover.jpg")': 'url("cover.jpg")',
        'url(/cover.jpg)': 'url(cover.jpg)',
        'href="/favicon.ico"': 'href="favicon.svg"',
        "href='/favicon.ico'": "href='favicon.svg'",
    }
    for old, new in replacements.items():
        index = index.replace(old, new)

    head_marker = "<head>"
    injection = (
        '<head>\n'
        '    <meta name="revcdos-pages-build" content="' + BUILD_VERSION + '">\n'
        '    <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 64 64\'%3E%3Crect width=\'64\' height=\'64\' rx=\'12\' fill=\'%23100731\'/%3E%3Ctext x=\'32\' y=\'42\' text-anchor=\'middle\' font-size=\'34\' fill=\'white\'%3EVC%3C/text%3E%3C/svg%3E">\n'
        '    <script>\n'
        '    (() => {\n'
        '      const params = new URLSearchParams(window.location.search);\n'
        '      const hasAuthorizedProxy = params.has("proxy") || localStorage.getItem("revcdos.proxy");\n'
        '      if (!hasAuthorizedProxy && params.get("request_original_game") !== "1") {\n'
        '        params.set("request_original_game", "1");\n'
        '        const next = window.location.pathname + "?" + params.toString() + window.location.hash;\n'
        '        window.location.replace(next);\n'
        '      }\n'
        '    })();\n'
        '    </script>\n'
        f'    <script src="coi-serviceworker.js?v={BUILD_VERSION}"></script>\n'
        f'    <script src="pages-config.js?v={BUILD_VERSION}"></script>'
    )
    index = replace_once(index, head_marker, injection, "index.html <head>")

    local_save_test = 'if (new URLSearchParams(window.location.search).get("custom_saves") === "1") {'
    if local_save_test in index:
        index = index.replace(local_save_test, 'if (false) { // local server saves are unavailable on GitHub Pages', 1)

    index_path.write_text(index, encoding="utf-8", newline="\n")

    shutil.copy2(wrapper / "pages-config.js", output / "pages-config.js")
    shutil.copy2(wrapper / "coi-serviceworker.js", output / "coi-serviceworker.js")
    shutil.copy2(wrapper / "favicon.svg", output / "favicon.svg")
    (output / ".nojekyll").write_text("", encoding="utf-8")

    build_info = {
        "pagesBuild": BUILD_VERSION,
        "upstreamRepository": "Lolendor/reVCDOS",
        "upstreamCommit": git_sha(upstream),
        "defaultDataMode": "request-original-game",
    }
    (output / "build-info.json").write_text(
        json.dumps(build_info, indent=2) + "\n",
        encoding="utf-8",
    )

    built_game = game_path.read_text(encoding="utf-8")
    built_index = index_path.read_text(encoding="utf-8")

    broken_root_asset_pattern = re.compile(
        r'''(?:src|href)=["']/+(?:cover\.jpg|intro\.mp4|favicon\.ico)["']|url\(\s*["']?/+(?:cover\.jpg|favicon\.ico)["']?\s*\)''',
        re.IGNORECASE,
    )

    checks = {
        "config injected": "REVCDOS_PAGES_CONFIG" in built_game,
        "vcbr is configurable": "pagesVcbrBase" in built_game,
        "original game mode injected": 'request_original_game' in built_index,
        "no broken root asset refs": not broken_root_asset_pattern.search(built_index),
        "cover exists": (output / "cover.jpg").is_file(),
        "intro exists": (output / "intro.mp4").is_file(),
        "favicon exists": (output / "favicon.svg").is_file(),
        "favicon embedded": 'data:image/svg+xml' in built_index,
        "COI worker included": f'src="coi-serviceworker.js?v={BUILD_VERSION}"' in built_index,
        "Pages config included": f'src="pages-config.js?v={BUILD_VERSION}"' in built_index,
        "build info exists": (output / "build-info.json").is_file(),
        "nojekyll exists": (output / ".nojekyll").exists(),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError("Build validation failed: " + ", ".join(failed))

    print(f"Built GitHub Pages site at: {output}")
    print(f"Upstream commit: {build_info['upstreamCommit']}")
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
