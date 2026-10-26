# -*- coding: utf-8 -*-
"""시안 HTML의 %%B64_<이름>%% 토큰을 docs/design/assets/<이름>.jpg|png 의 data URI로 치환.

원본(screen-mockup.html)은 그대로 두고 screen-mockup.built.html 로 쓴다 (빌드 결과는 커밋 안 함).
맥·윈도우 공통: python tools/build_mockup.py
"""
import base64
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "docs" / "design"
SRC = ROOT / "screen-mockup.html"
OUT = ROOT / "screen-mockup.built.html"
ASSETS = ROOT / "assets"
MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}

if not SRC.exists():
    sys.exit(f"시안 파일이 없음: {SRC}")
text = SRC.read_text(encoding="utf-8")
tokens = set(re.findall(r"%%B64_(\w+)%%", text))
if not tokens:
    OUT.write_text(text, encoding="utf-8")
    print(f"토큰 없음 — 그대로 복사: {OUT}")
    sys.exit(0)
for name in sorted(tokens):
    found = [p for p in ASSETS.glob(f"{name}.*") if p.suffix.lower() in MIME]
    if not found:
        sys.exit(f"에셋 없음: {ASSETS / name}.(jpg|png|webp)")
    img = found[0]
    b64 = base64.b64encode(img.read_bytes()).decode()
    text = text.replace(f"%%B64_{name}%%", f"data:{MIME[img.suffix.lower()]};base64,{b64}")
OUT.write_text(text, encoding="utf-8")
size_kb = OUT.stat().st_size // 1024
print(f"빌드 완료: {len(tokens)}개 이미지 임베드 → {OUT} ({size_kb}KB{' — 16MB 초과!' if size_kb > 16 * 1024 else ''})")
