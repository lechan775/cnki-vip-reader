<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/OpenHanako-Skill-6c5ce7?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHJ4PSI2IiBmaWxsPSIjNmM1Y2U3Ii8+PHRleHQgeD0iMTIiIHk9IjE2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSJ3aGl0ZSIgZm9udC1zaXplPSIxMiIgZm9udC1mYW1pbHk9InNhbnMtc2VyaWYiPuWTpjwvdGV4dD48L3N2Zz4=">
  <source media="(prefers-color-scheme: light)" srcset="https://img.shields.io/badge/OpenHanako-Skill-6c5ce7?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHJ4PSI2IiBmaWxsPSIjNmM1Y2U3Ii8+PHRleHQgeD0iMTIiIHk9IjE2IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSJ3aGl0ZSIgZm9udC1zaXplPSIxMiIgZm9udC1mYW1pbHk9InNhbnMtc2VyaWYiPuWTpjwvdGV4dD48L3N2Zz4=">
  <img alt="OpenHanako Skill" src="https://img.shields.io/badge/OpenHanako-Skill-6c5ce7?style=for-the-badge">
</picture>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Platform: OpenHanako](https://img.shields.io/badge/Platform-OpenHanako-6c5ce7)](https://github.com/liliMozi/openhanako)

</div>

<br>

# CNKI-VIP Reader

中文文献自动检索与阅读 Skill —— 基于 OpenHanako 平台的知网/维普学术论文全流程 Agent。

`cnki-vip-reader` 使 AI Agent 能够**自动登录**中文文献中转平台、**批量检索**知网与维普、**下载 PDF 全文**并**结构化阅读**。针对知网 PDF 专有字体编码乱码问题，内置**多模态视觉回退**机制，通过临时视觉子 Agent 截图识别，彻底绕过传统 OCR 限制。

## 📄 文档

<details open>
<summary>快速开始</summary>

### 安装

将本仓库克隆到 OpenHanako 的 skills 目录：

```bash
# 克隆到全局技能库
git clone https://github.com/lechan775/cnki-vip-reader \
  ~/.hanako/skills/cnki-vip-reader

# 或手动复制到 OpenHanako 的 skill 目录
cp -r cnki-vip-reader/ ~/.hanako/skills/
```

安装 Python 依赖：

```bash
pip install playwright
playwright install chromium
```

### 配置

```bash
# 复制配置文件
cp config.example.json config.json

# 编辑配置，填入中转平台凭据
{
    "username": "your_account",
    "password": "your_password"
}
```

也可通过环境变量设置：

```bash
export RELAY_USERNAME="your_account"
export RELAY_PASSWORD="your_password"
```

### 使用

在 OpenHanako 对话中直接说：

```
「知网搜一下 Transformer 注意力机制」
「维普检索 轻量化人脸识别」
「下载选中的第 1、3、5 篇」
```

Agent 会自动触发 Skill，执行检索→下载→阅读全流程。

</details>

## ✨ 特性

| 特性 | 说明 |
|------|------|
| 🔍 **双库检索** | 同时检索知网 (CNKI) 和维普 (VIP)，输出结构化题录 |
| 📥 **无弹窗下载** | Playwright 脚本自动 cookie 注入，绕过下载弹窗确认 |
| 📖 **全文阅读** | 集成 `nature-reader` 中英对照解读、`office-documents` 文本提取 |
| 🖼️ **多模态回退** | 知网 PDF 乱码时自动截图 → 视觉子 Agent 识别，无需手动转换 |
| 🔐 **Cookie 复用** | 登录一次即可，后续操作跳过验证码 |
| ⚡ **代理模式** | 通过第三方文献云中转，无需机构 VPN |

## 🏗️ 架构

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   OpenHanako  │────▶│  cnki-vip-   │────▶│  文献云中转   │
│   Agent       │◀────│  reader      │◀────│  (自部署)     │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                   ┌────────▼────────┐
                   │  Playwright     │
                   │  无头浏览器下载  │
                   └────────┬────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
         ┌────────┐  ┌──────────┐  ┌──────────┐
         │ 知网CAJ │  │ 维普 PDF │  │ 截图回退  │
         └────┬───┘  └────┬─────┘  └────┬─────┘
              │            │             │
              ▼            ▼             ▼
         ┌──────────────────────────────────┐
         │  nature-reader / office-documents │
         │  结构化全文解读                    │
         └──────────────────────────────────┘
```

## 🚀 工作流

### 阶段 1: 登录中转平台
Agent 自动填入凭据 → OCR 识别验证码 → Cookie 持久化

### 阶段 2A: 知网检索
进入知网代理 → 关键词搜索 → 题录提取 → CAJ/PDF 下载

### 阶段 2B: 维普检索 (推荐)
进入维普 → CARSI 认证 → 搜索 → PDF 全文下载

### 阶段 3: 阅读
PDF 到位后自动调用 `nature-reader` → 中英对照全文解读

### 阶段 4: 多模态回退 (知网乱码专用)
```
PDF 截图 → subagent wujie (GPT-5.5 视觉) → 逐页文字识别 → 汇总 .md
```

## 📊 支持平台与方法

| 平台 | 检索 | 题录 | PDF下载 | CAJ下载 | 乱码方案 |
|------|:----:|:----:|:------:|:------:|----------|
| **维普 (VIP)** | ✅ | ✅ | ✅ (Playwright) | N/A | N/A (标准PDF) |
| **知网 (CNKI)** | ✅ | ✅ | ⚠️ 乱码 | ✅ | 阶段4 截图+视觉识别 |

## ⚠️ 前置要求

> **本仓库不包含文献云中转平台本身。** 您需要自建或获取一个类似「文献云」的中转平台，该平台需支持：
> - 知网代理（反向代理到知网搜索界面）
> - 维普 CARSI 机构认证
> - 用户登录与 cookie 管理

部署后将 SKILL.md 中的 `YOUR_RELAY_HOST`、`YOUR_CNKI_PROXY` 等占位符替换为实际地址。

## 📦 文件结构

```
cnki-vip-reader/
├── README.md                     ← 本文件
├── SKILL.md                      ← Skill 核心工作流定义
├── LICENSE                       ← MIT License
├── .gitignore
├── config.example.json           ← 凭据配置模板
└── scripts/
    └── download_vip_pdf.py       ← 无弹窗 PDF/CAJ 下载脚本
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。

- 报告 Bug → [GitHub Issues](https://github.com/lechan775/cnki-vip-reader/issues)
- 贡献代码 → Fork → Feature Branch → PR
- 分享您的中转平台适配配置

## 📄 License

MIT © 2025 Guowei Jiang ([@lechan775](https://github.com/lechan775))
