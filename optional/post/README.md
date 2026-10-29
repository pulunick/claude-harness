# optional/post — SNS 게시물 프로젝트 모듈 (글 + 짧은 세로 영상)

film 모듈의 게시물형 변형(2026-10-29, 쇼룸에서 나옴). film이 유튜브 회차·`film/` 상위 폴더(포트 배정표·`/update` 도구)를 전제로 하는 데 비해, 이 모듈은 **어디에 두든 혼자 서는** 게시물 채널 뼈대다. 보통 `craft` 모듈과 같이 켠다. film과 같이 켜지 않는다.

## 켜기

```bash
python3 <harness>/setup/sync.py init <폴더> --profile solo --with craft,post --title "<채널 이름>"
```

하는 일: `tools/craft.sh`(공용, film과 같은 파일) · CLAUDE.md에 "SNS 게시물 프로젝트" 절(세로 1080×1920·자막 필수 기본) · `docs/{00_채널,01_게시물,02_아이디어,03_편집}` `media/{원본,내보내기/…}` `edit/{film,effect,motion}` 폴더 · 게시물 틀 `docs/01_게시물/_틀.md` · 게시물용 STATE 뼈대 · `.mcp.json`(craft가 있으면 craft의 headless 본, 포트 자리표시자 없음).

## 공용 vs 소유

| 공용 (sync가 갱신) | 소유 (한 번 만들고 프로젝트가 관리) |
|---|---|
| `tools/craft.sh` | CLAUDE.md 절, `.mcp.json`, STATE·게시물 틀(`skeleton/`) |
