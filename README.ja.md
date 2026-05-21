<div align="center">

[🇬🇧 English](README.md) | [🇨🇳 简体中文](README.zh-CN.md) | [🇯🇵 日本語](README.ja.md) | [🇰🇷 한국어](README.ko.md)

<br>

<img src="assets/social-preview.png" alt="CNKI-VIP Reader" width="640">

<br>

[![AI Agent Skill](https://img.shields.io/badge/AI_Agent-Skill-6c5ce7?style=for-the-badge)](https://github.com/lechan775/cnki-vip-reader)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge)](https://www.python.org/)
[![対応: 全エージェント](https://img.shields.io/badge/対応-全エージェント-2ea44f?style=for-the-badge)](https://github.com/lechan775/cnki-vip-reader)

</div>

<br>

# CNKI-VIP Reader

**AIエージェント向け中国学術文献自動検索・読解スキル**

`cnki-vip-reader` は、あらゆるAIエージェントが中国文献中継プラットフォームに**自動ログイン**し、CNKI（知網）とVIP（維普）を**一括検索**、**PDFフルテキストをダウンロード**して**構造的に読解**することを可能にします。CNKIの独自フォントエンコーディングによる文字化けには、**マルチモーダル視覚フォールバック**機構を内蔵し、視覚サブエージェントによるスクリーンショット認識で従来のOCR制限を完全に回避します。

### 🎯 あらゆるエージェントプラットフォームで動作

本スキルはプラットフォーム非依存のワークフロー仕様として記述されています。エージェントが**ブラウザ**ツール（Playwright/Puppeteer）と**bash/shell**ツールにアクセスできれば動作します：

| プラットフォーム | 状況 |
|------------------|------|
| **OpenHanako** | ✅ 完全対応 — `browser` + `bash` + `subagent` |
| **Claude Code** | ✅ `bash` ツール + カスタム Playwright MCP |
| **Codex / Hana** | ✅ `browser` + `bash` + `subagent` |
| **カスタム MCP Agent** | ✅ ブラウザ自動化機能を持つ任意のエージェント |
| **LangChain / CrewAI** | ✅ SKILL.md をお使いのエージェントのツール定義に適合 |

> **コアワークフローは `SKILL.md` に定義されています——人間にも機械にも読める指示ファイルです。** ツール呼び出し（`browser start`、`bash`、`web_search`）をお使いのエージェントプラットフォームの対応ツールにマッピングするだけです。

## ✨ 主な機能

| 機能 | 説明 |
|------|------|
| 🔍 **デュアルデータベース検索** | CNKIとVIPを同時検索、構造化書誌情報を出力 |
| 📥 **ポップアップなしダウンロード** | PlaywrightスクリプトによるCookie注入でダウンロード確認を回避 |
| 📖 **フルテキスト読解** | 構造化読解、日中対訳対応 |
| 🖼️ **マルチモーダルフォールバック** | CNKIフォント文字化け時にスクリーンショット→視覚サブエージェント認識 |
| 🔐 **Cookie再利用** | 初回ログイン後、CAPTCHAをスキップ |
| ⚡ **リレーモード** | サードパーティ中継経由、機関VPN不要 |
| 🌐 **プラットフォーム非依存** | OpenHanako、Claude、Codexなど、ブラウザ+Shellツールを持つ任意のエージェントで動作 |

## 🚀 クイックスタート

```bash
pip install playwright && playwright install chromium
cp config.example.json config.json
# config.json に中継プラットフォームの認証情報を記入
```

エージェントに Skill を渡す：

```bash
# OpenHanako
cp -r cnki-vip-reader/ ~/.hanako/skills/

# Claude Code
claude --custom-instructions ./SKILL.md

# カスタム Agent → SKILL.md をシステムプロンプトに注入
```

使用例：

```
「CNKIでTransformerのアテンション機構を検索して」
「VIPで軽量顔認識を検索」
「論文1、3、5番をダウンロード」
```

## 📬 お問い合わせ

設定で問題が発生した場合は、QQ にてご連絡ください：

- **QQ**: 3297767619
- **ニックネーム**: unique&williams

## 📄 License

MIT © 2025 Guowei Jiang ([@lechan775](https://github.com/lechan775))
