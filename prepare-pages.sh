#!/usr/bin/env bash
set -euo pipefail
rm -rf upstream public
git clone --depth 1 https://github.com/Lolendor/reVCDOS.git upstream
python3 build_pages.py upstream public
echo
echo "Ready: ./public"
echo "For a quick local test: python3 -m http.server 8000 --directory public"
