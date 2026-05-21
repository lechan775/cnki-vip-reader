<div align="center">

[🇬🇧 English](README.md) | [🇨🇳 简体中文](README.zh-CN.md) | [🇯🇵 日本語](README.ja.md) | [🇰🇷 한국어](README.ko.md)

<br>

<img src="assets/social-preview.png" alt="CNKI-VIP Reader" width="640">

<br>

[![AI Agent Skill](https://img.shields.io/badge/AI_Agent-Skill-6c5ce7?style=for-the-badge)](https://github.com/lechan775/cnki-vip-reader)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge)](https://www.python.org/)
[![适用: 任意智能体](https://img.shields.io/badge/适用-任意智能体-2ea44f?style=for-the-badge)](https://github.com/lechan775/cnki-vip-reader)

</div>

<br>

# CNKI-VIP Reader

**面向 AI 智能体的中文文献自动检索与阅读 Skill**

`cnki-vip-reader` 让任意 AI 智能体能够**自动登录**中文文献中转平台、**批量检索**知网与维普、**下载 PDF 全文**并**结构化阅读**。针对知网 PDF 专有字体编码乱码问题，内置**多模态视觉回退**机制，通过视觉子智能体截图识别，彻底绕过传统 OCR 限制。

### 🎯 适用于任意智能体平台

本 Skill 以平台无关的工作流规范编写。只要你的智能体能调用**浏览器**工具（Playwright/Puppeteer）和 **bash/shell** 工具即可运行：

| 平台 | 状态 |
|------|------|
| **OpenHanako** | ✅ 完整支持 — `browser` + `bash` + `subagent` |
| **Claude Code** | ✅ `bash` 工具 + 自定义 Playwright MCP |
| **Codex / Hana** | ✅ `browser` + `bash` + `subagent` |
| **自定义 MCP Agent** | ✅ 任何具备浏览器自动化能力的智能体 |
| **LangChain / CrewAI** | ✅ 将 SKILL.md 适配到你的智能体工具定义 |

> **核心工作流定义在 `SKILL.md` 中——一份人类和机器均可读的指令文件。** 你只需将工具调用（`browser start`、`bash`、`web_search`）映射到你智能体平台的对应工具即可。

## 📄 文档

<details open>
<summary>快速开始</summary>

### 安装依赖

```bash
pip install playwright
playwright install chromium
```

### 配置

```bash
cp config.example.json config.json
# 编辑 config.json，填入中转平台凭据
```

或通过环境变量设置：

```bash
export RELAY_USERNAME="your_account"
export RELAY_PASSWORD="your_password"
```

### 将 Skill 交给你的智能体

**OpenHanako** — 复制到 skills 目录：
```bash
cp -r cnki-vip-reader/ ~/.hanako/skills/
```

**Claude Code** — 添加到 CLAUDE.md 或作为项目 Skill：
```bash
claude --custom-instructions ./SKILL.md
```

**自定义 Agent** — 将 SKILL.md 注入智能体的系统提示词或工具上下文。

### 使用

直接对智能体说：

```
「知网搜一下 Transformer 注意力机制」
「维普检索 轻量化人脸识别」
「下载第 1、3、5 篇」
```

智能体读取 SKILL.md 并自动执行工作流。

</details>

## ✨ 特性

| 特性 | 说明 |
|------|------|
| 🔍 **双库检索** | 同时检索知网 (CNKI) 和维普 (VIP)，输出结构化题录 |
| 📥 **无弹窗下载** | Playwright 脚本自动 cookie 注入，绕过下载弹窗确认 |
| 📖 **全文阅读** | 结构化全文解读，支持中英对照 |
| 🖼️ **多模态回退** | 知网 PDF 乱码时自动截图 → 视觉子智能体识别，无需手动转换 |
| 🔐 **Cookie 复用** | 登录一次即可，后续操作跳过验证码 |
| ⚡ **代理模式** | 通过第三方文献云中转，无需机构 VPN |
| 🌐 **平台无关** | 适用于 OpenHanako、Claude、Codex 等任意具备浏览器+Shell 工具的智能体 |

## 🏗️ 架构

```
┌──────────────────┐     ┌──────────────┐     ┌──────────────┐
│  任意 AI 智能体   │────▶│  cnki-vip-   │────▶│  文献云中转   │
│  (OpenHanako/    │◀────│  reader      │◀────│  (自行部署)   │
│   Claude/Codex)  │     └──────┬───────┘     └──────────────┘
└──────────────────┘            │
                   ┌────────────▼────────────┐
                   │  Playwright 无头浏览器    │
                   │  (下载 PDF)              │
                   └────────────┬────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
         ┌────────┐      ┌──────────┐      ┌──────────┐
         │知网 CAJ │      │ 维普 PDF │      │ 截图回退  │
         │  下载   │      │   下载   │      │          │
         └────┬───┘      └────┬─────┘      └────┬─────┘
              │                │                  │
              ▼                ▼                  ▼
         ┌──────────────────────────────────────────┐
         │        结构化全文阅读与分析                 │
         └──────────────────────────────────────────┘
```

## 🚀 工作流

| 阶段 | 操作 |
|------|------|
| **1. 登录** | 智能体自动填入凭据 → OCR 识别验证码 → Cookie 持久化 |
| **2A. 知网检索** | 进入知网代理 → 关键词搜索 → 题录提取 → 下载 |
| **2B. 维普检索**（推荐） | 进入维普 → CARSI 认证 → 搜索 → PDF 下载 |
| **3. 阅读** | PDF 提取 → 结构化全文解读 |
| **4. 回退** | 知网字体乱码 → 逐页截图 → 视觉子智能体 OCR → 汇总 .md |

## 📊 支持平台与方法

| 平台 | 检索 | 题录 | PDF下载 | CAJ下载 | 乱码方案 |
|------|:----:|:----:|:------:|:------:|----------|
| **维普 (VIP)** | ✅ | ✅ | ✅ Playwright | N/A | N/A (标准PDF) |
| **知网 (CNKI)** | ✅ | ✅ | ⚠️ 乱码 | ✅ | 阶段4 截图+视觉识别 |

## ⚠️ 前置要求

> **本仓库不包含文献云中转平台本身。** 你需要自建或获取一个类似「文献云」的中转平台，该平台需支持：
> - 知网代理（反向代理到知网搜索界面）
> - 维普 CARSI 机构认证
> - 用户登录与 cookie 管理

部署后将 SKILL.md 中的 `YOUR_RELAY_HOST`、`YOUR_CNKI_PROXY` 等占位符替换为实际地址。

## 📦 文件结构

```
cnki-vip-reader/
├── README.md                     ← 英文版
├── README.zh-CN.md               ← 简体中文（本文件）
├── README.ja.md                  ← 日本語
├── README.ko.md                  ← 한국어
├── SKILL.md                      ← 核心工作流规范
├── LICENSE                       ← MIT License
├── assets/
│   └── social-preview.png        ← 仓库封面图
├── .gitignore
├── config.example.json           ← 凭据配置模板
└── scripts/
    └── download_vip_pdf.py       ← 无弹窗 PDF/CAJ 下载脚本
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。

- 报告 Bug → [GitHub Issues](https://github.com/lechan775/cnki-vip-reader/issues)
- 贡献代码 → Fork → Feature Branch → PR
- 分享你的中转平台适配配置
- 帮助翻译 README 到更多语言

## 📄 License

MIT © 2025 Guowei Jiang ([@lechan775](https://github.com/lechan775))
