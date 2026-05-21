<div align="center">

[🇬🇧 English](README.md) | [🇨🇳 简体中文](README.zh-CN.md) | [🇯🇵 日本語](README.ja.md) | [🇰🇷 한국어](README.ko.md)

<br>

<img src="assets/social-preview.png" alt="CNKI-VIP Reader" width="640">

<br>

[![AI Agent Skill](https://img.shields.io/badge/AI_Agent-Skill-6c5ce7?style=for-the-badge)](https://github.com/lechan775/cnki-vip-reader)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge)](https://www.python.org/)
[![호환: 모든 에이전트](https://img.shields.io/badge/호환-모든_에이전트-2ea44f?style=for-the-badge)](https://github.com/lechan775/cnki-vip-reader)

</div>

<br>

# CNKI-VIP Reader

**AI 에이전트를 위한 중국 학술 문헌 자동 검색 및 독해 스킬**

`cnki-vip-reader`는 모든 AI 에이전트가 중국 문헌 중계 플랫폼에 **자동 로그인**하고, CNKI(知網)와 VIP(維普)를 **일괄 검색**하며, **PDF 전문을 다운로드**하여 **구조적으로 독해**할 수 있게 합니다. CNKI의 독자적인 폰트 인코딩으로 인한 문자 깨짐 현상에는 **멀티모달 시각 폴백** 메커니즘을 내장하여, 시각 서브 에이전트의 스크린샷 인식으로 기존 OCR의 한계를 완전히 우회합니다.

### 🎯 모든 에이전트 플랫폼에서 실행 가능

본 스킬은 플랫폼 독립적인 워크플로우 명세로 작성되었습니다. 에이전트가 **브라우저** 도구(Playwright/Puppeteer)와 **bash/shell** 도구에 접근할 수 있으면 작동합니다:

| 플랫폼 | 상태 |
|--------|------|
| **OpenHanako** | ✅ 완전 지원 — `browser` + `bash` + `subagent` |
| **Claude Code** | ✅ `bash` 도구 + 커스텀 Playwright MCP |
| **Codex / Hana** | ✅ `browser` + `bash` + `subagent` |
| **커스텀 MCP Agent** | ✅ 브라우저 자동화 기능을 갖춘 모든 에이전트 |
| **LangChain / CrewAI** | ✅ SKILL.md를 에이전트 도구 정의에 맞게 조정 |

> **핵심 워크플로우는 `SKILL.md`에 정의되어 있습니다——사람과 기계 모두 읽을 수 있는 명령 파일입니다.** 도구 호출(`browser start`, `bash`, `web_search`)을 사용 중인 에이전트 플랫폼의 해당 도구에 매핑하기만 하면 됩니다.

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| 🔍 **듀얼 데이터베이스 검색** | CNKI와 VIP 동시 검색, 구조화된 서지 정보 출력 |
| 📥 **팝업 없는 다운로드** | Playwright 스크립트의 Cookie 주입으로 다운로드 확인 우회 |
| 📖 **전문 독해** | 구조화된 독해, 중영 대역 지원 |
| 🖼️ **멀티모달 폴백** | CNKI 폰트 깨짐 시 스크린샷 → 시각 서브 에이전트 인식 |
| 🔐 **Cookie 재사용** | 최초 로그인 후 CAPTCHA 건너뛰기 |
| ⚡ **릴레이 모드** | 서드파티 중계 경유, 기관 VPN 불필요 |
| 🌐 **플랫폼 독립적** | OpenHanako, Claude, Codex 등 브라우저+Shell 도구를 가진 모든 에이전트에서 작동 |

## 🚀 빠른 시작

```bash
pip install playwright && playwright install chromium
cp config.example.json config.json
# config.json에 중계 플랫폼 인증 정보 입력
```

에이전트에 Skill 전달:

```bash
# OpenHanako
cp -r cnki-vip-reader/ ~/.hanako/skills/

# Claude Code
claude --custom-instructions ./SKILL.md

# 커스텀 Agent → SKILL.md를 시스템 프롬프트에 주입
```

사용 예:

```
"CNKI에서 Transformer 어텐션 메커니즘 검색해 줘"
"VIP에서 경량 얼굴 인식 검색"
"논문 1, 3, 5번 다운로드"
```

## 📬 문의

설정 중 문제가 발생하면 QQ로 연락해 주세요:

- **QQ**: 3297767619
- **닉네임**: unique&williams

## 📄 License

MIT © 2025 Guowei Jiang ([@lechan775](https://github.com/lechan775))
