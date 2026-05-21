# CNKI-VIP Reader — 知网/维普中文文献自动检索与阅读

面向 OpenHanako 平台的可移植 Skill。使 Agent 能够通过第三方中转平台自动登录、检索、下载和阅读知网与维普的中文学术文献。

## 触发条件

用户提及以下任一关键词时激活：
- 「知网」「CNKI」「中国知网」
- 「维普」「VIP」「cqvip」
- 「中文文献」「中文论文」
- 「检索一下中文」「查一下国内论文」

## 前置依赖

Agent 在首次使用前需确认环境：

### 必需
- `browser` 工具可用（基于 Playwright 的无头浏览器）
- `bash` 工具可用
- Python 3.8+ 及 `playwright` 包

### 推荐（多模态回退）
- 无需额外配置。阶段 4 自动通过 `subagent agent="wujie"` 创建临时视觉智能体读取截图
- wujie 是 OpenHanako 预置 agent（GPT-5.5），无需手动创建
- 任务完成后子 agent 自动销毁，无残留

### 检查命令
```bash
python -c "import playwright; print('OK')" 2>/dev/null || pip install playwright && playwright install chromium
```

## 凭据配置

Agent 在执行任何操作前，需获取中转平台的登录凭据：

### 优先级
1. **环境变量**：`RELAY_USERNAME` / `RELAY_PASSWORD`
2. **配置文件**：`<skill_dir>/config.json`，格式 `{"username":"xxx","password":"xxx"}`
3. **交互询问**：若无以上配置，向用户索要

Agent 首次获取凭据后应缓存到 `config.json`（若用户同意）。

## 中转平台 URL 配置

本 Skill 假设您已部署或拥有一个 CNKI/VIP 文献云中转平台（类似文献云）。部署前请将以下 URL 替换为实际地址：

| 占位符 | 说明 | 替换为 |
|--------|------|--------|
| `YOUR_RELAY_HOST` | 文献云中转平台域名 | e.g. `lib.example.com` |
| `YOUR_CNKI_PROXY` | 知网代理地址 (IP:port) | e.g. `192.168.1.100:9299` |
| `YOUR_INSTITUTION` | CARSI 认证机构名 | e.g. `北京大学` |
| `YOUR_IDP_DOMAIN` | 机构 SSO 域名 | e.g. `idp.pku.edu.cn` |

> **开源版不含中转平台本身**。中转平台的搭建与部署不在本项目的覆盖范围内——本 Skill 仅负责 Agent 侧的自动化检索与阅读。

## 工作流

### 阶段 1：登录中转平台

```
browser start → navigate http://YOUR_RELAY_HOST/e/member/login/
```

1. 填入用户名 + 密码
2. **关键**：验证码需 OCR 识别。Agent 应截图 → 读取验证码图片 → 填入
3. 点击「立即登录」
4. 若登录成功 → 进入资源列表；若失败 → 重试（最多3次），每次刷新验证码

**注意**：Cookie 有效期较长（首次登录后短期无需重复登录）。

**重要 — Cookie 复用**：登录成功后，Agent 执行 `browser evaluate → document.cookie` 提取 cookie 字符串，保存到临时变量。后续所有下载操作通过 `--cookie` 参数传递给 Playwright 脚本，**跳过验证码**。

---

### 阶段 2A：知网 (CNKI) 检索

```
navigate http://YOUR_RELAY_HOST/e/action/ListInfo/?classid=61
click "知网入口"
# 此时进入知网检索界面 http://YOUR_CNKI_PROXY/kns8s/defaultresult/index
```

1. 在搜索框输入检索词 → 点击搜索
2. 从结果页提取题录：**标题、作者、来源、日期、被引量、资源类型**
3. 可选使用左侧分面筛选（学位论文/学术期刊/年份等）
4. 用 `browser snapshot` 获取当前页文献列表，返回给用户筛选

**题录提取格式**（结构化输出给用户）：
```
[1] 标题 | 作者 | 来源 | 日期 | 被引量 | 类型
[2] ...
```

#### 知网全文获取与自动下载

**自动下载方案（无弹窗）**：
1. Agent 在 browser 中进入知网检索结果页
2. 点击目标论文的「下载CAJ格式」或「原版阅读」→ 触发下载
3. 若弹窗要求手动确认 → 提取 browser cookie → 调用 Playwright 脚本：
```bash
python <skill_dir>/scripts/download_vip_pdf.py \
  --source cnki \
  --url "<知网下载URL>" \
  --output "D:/papers/论文名.caj" \
  --cookie "<从browser提取的cookie>"
```

**⚠️ 知网 PDF 字体编码问题**：即使成功下载 PDF，PyMuPDF/pdfplumber 提取的中文大概率是乱码（知网使用非标准字体编码）。**此时自动跳转阶段 4（多模态回退）**

**替代方案**：
- 优先用维普下载同篇论文的标准 PDF
- 用户手动用 CAJViewer 打开 → Ctrl+A 复制 → 保存为 .txt
- 阶段 4 多模态截图识别

---

### 阶段 2B：维普 (VIP) 检索（推荐，因输出 PDF）

```
navigate http://YOUR_RELAY_HOST/e/action/ListInfo/?classid=61
click "维普入口"
# 进入维普中转页
```

**维普 CARSI 认证流程**：
1. 点击「第一步点我」→ 弹出机构 SSO 页面 → **不输入任何凭据** → 直接返回
2. 点击「第二步点我」→ 若显示「Accept」按钮 → 点击 Accept → 进入维普首页
3. 若显示「Stale Request」错误 → 改用 `navigate http://qikan.cqvip.com/index.html`（Cookie可能仍有效）
4. 确认页面顶部显示机构名称即登录成功

**检索**：
1. 搜索框输入检索词 → 点击检索
2. 结果页含摘要预览、期刊、收录类别（北大核心/CSCD等）
3. 每篇均有「在线阅读」和「下载PDF」按钮
4. 题录提取格式同知网

#### 维普 PDF 全文获取（推荐路径）

**方案 A — Playwright 脚本自动下载（无弹窗）**：Agent 提取 browser cookie → 调用脚本 → accept_downloads 自动保存 PDF

**方案 B — pdf.js 文本提取**：点击「在线阅读」→ pdf.js 渲染 → evaluate `getTextContent()` 逐页提取文本 → 保存 .md（无需下载文件）

**方案 C — 在线阅读器截图**（备用）：`browser screenshot` 获取视觉内容，适合快速浏览

**方案 A 详细流程**：
```bash
# Step 1: 在 browser 中提取 cookie
browser evaluate → document.cookie
# 返回: "key1=val1; key2=val2; ..."

# Step 2: 用脚本下载（无弹窗自动保存）
python <skill_dir>/scripts/download_vip_pdf.py \
  --source vip \
  --url "http://qikan.cqvip.com/Qikan/Article/ReadIndex?id=XXXX" \
  --output "D:/papers/论文名.pdf" \
  --cookie "XXXXX..."
```

---

### 阶段 3：阅读已下载文献

PDF 文件到位后：
- `nature-reader` skill：中英对照全文解读、图表提取
- `office-documents` skill：纯文本提取、段落分析
- 多篇对比阅读时可选向量化（Chroma/Faiss），但单篇直接全文输入即可

**⚠️ 知网 PDF 乱码检测**：若 PyMuPDF/pdfplumber 提取的文本中连续出现无法解析的字符（如 `□□□`、`脙鈥⒚Ｄ` 等），且可读中文占比 < 5%，判定为知网专有字体编码乱码。此时**自动进入阶段 4**。

---

### 阶段 4：多模态回退 — 知网 PDF / CAJ 乱码补救

当文本提取工具因知网专有字体编码导致乱码时，切换到**浏览器截图 + 临时视觉子 Agent**路径。

#### 原理

OpenHanako 支持创建临时视觉辅助智能体。即使主模型（如 DeepSeek）不支持图像输入，也可以通过 `subagent` 调用 `wujie`（GPT-5.5，支持多模态），读取截图后返回文本，任务完成后自动销毁。

**无需用户手动切换模型。**

#### 工作流

**Step 1 — 截图**（主 Agent 执行）：
```
browser start
  → navigate file:///D:/path/to/论文.pdf    # 浏览器打开本地 PDF
    或 navigate <知网在线阅读URL>            # 在线打开
  → wait 3s 等待 PDF 渲染
  → 检测 PDF 总页数（通过页面内页码元素）
  → 循环逐页：
       screenshot → 保存为 <output_dir>/_screenshots/page_N.png
       scroll down 或 click 下一页按钮
       间隔 1s 等待渲染
  → browser stop
```

**Step 2 — 识别**（主 Agent 调用视觉子 Agent）：

首选方案 — 调用 wujie（OpenHanako 预置，GPT-5.5 视觉）：
```
subagent agent="wujie" task="
  任务：读取论文截图并识别所有文字
  
  请依次读取以下截图文件，逐页识别其中的文字内容：
  1. <output_dir>/_screenshots/page_001.png
  2. <output_dir>/_screenshots/page_002.png
  ...
  
  要求：
  - 使用 read 工具读取每张图片
  - 识别出图片中的所有中英文文字、数字、公式
  - 按页码顺序输出，格式：
    === 第 N 页 ===
    [识别内容]
  - 完成后不要做总结，只输出原始文字即可
"
```

若 subagent wujie 不可用（极简部署环境），回退方案：
- 若当前模型本身支持图像（GPT-4o / Claude / Gemini）→ 直接用 `read` 工具读取截图
- 若当前模型不支持图像 → 告知用户：「当前环境无视觉 Agent，请将模型切换为 GPT-4o 或 Claude 后重试」

**Step 3 — 汇总**（主 Agent 执行）：
- 接收 wujie 返回的逐页文本
- 合并为完整全文
- `write` 保存为 `<output_dir>/论文名_全文.md`
- 清理 `_screenshots/` 临时目录

---

## 已知限制与对策

| 限制 | 影响 | 对策 |
|------|------|------|
| 验证码 | 登录被阻断 | Agent OCR 自动识别；失败时请求人工辅助 |
| CAJ 格式 | 知网全文不可直接读 | `caj2pdf` 转换；或优先用维普 |
| Stale SAML | 维普 CARSI 过期 | 重新走第一步→第二步→Accept 流程 |
| 下载弹窗需手动确认 | browser 工具未配置 accept_downloads | 提取 cookie → Playwright 脚本自动下载，无弹窗 |
| 频率限制 | 短时间大量检索/下载触发封禁 | 检索间隔 ≥ 5s，下载间隔 ≥ 30s |
| 并发下载 | 知网封 IP | 坚决禁止并发，串行执行 |
| 知网 PDF 字体编码乱码 | PyMuPDF/pdfplumber 提取中文全部乱码 | 自动切换阶段 4：浏览器截图 + subagent wujie 视觉识别 |

---

## 依赖安装

在目标机器上首次部署时，Agent 需执行：

```bash
pip install playwright
playwright install chromium
```

无需额外系统依赖。

---

## 输出规范

Agent 检索完成后，向用户呈现结构化结果：

```
### 知网检索：「XXX」— 学术期刊 N 篇，学位论文 M 篇

| # | 标题 | 作者 | 来源 | 日期 | 被引 |
|---|------|------|------|------|------|
| 1 | ... | ... | ... | ... | ... |

### 维普检索：「XXX」— N 篇

| # | 标题 | 作者 | 来源 | 收录 | 日期 |
|---|------|------|------|------|------|
| 1 | ... | ... | ... | 北大核心 | ... |

请选择要下载的编号（支持多选如 1,3,5），或输入「全部」
```

用户选定后，Agent 依次下载并存储到用户指定目录。
