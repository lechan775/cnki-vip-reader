#!/usr/bin/env python3
"""
维普/知网 PDF 全文自动下载脚本（无弹窗）
利用 Playwright accept_downloads 自动保存文件，无需手动确认。

用法（推荐 — cookie 复用模式）:
    python download_vip_pdf.py \
      --url "http://qikan.cqvip.com/Qikan/Article/ReadIndex?id=XXXX" \
      --output "./论文.pdf" \
      --cookie "key1=val1; key2=val2; ..."

用法（完整登录模式 — 需要验证码）:
    python download_vip_pdf.py \
      --url "..." --output "..." \
      --username "your_account" --password "xxx"

cookie 获取方式：
    在 OpenHanako browser 会话中执行: document.cookie
    将返回的完整字符串传给 --cookie 参数即可。

依赖: pip install playwright && playwright install chromium

环境变量:
    RELAY_USERNAME   中转平台用户名
    RELAY_PASSWORD   中转平台密码
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, unquote

# ============ 部署前请修改 ============
# 这些域名用于 cookie 注入时的 domain 推断
# 请替换为您的实际中转平台及机构域名
RELAY_DOMAINS = [
    "cqvip.com", "qikan.cqvip.com",
    "your-relay-host.example.com",
    "your-idp-domain.example.com",
    "cnki.net",
]
# ====================================


def parse_cookie_string(cookie_str):
    """将 document.cookie 字符串解析为 Playwright cookie 对象列表"""
    cookies = []
    for item in cookie_str.split(";"):
        item = item.strip()
        if "=" not in item:
            continue
        key, _, val = item.partition("=")
        key = key.strip()
        val = unquote(val.strip())
        cookies.append({
            "name": key,
            "value": val,
            "domain": "",
            "path": "/",
        })
    return cookies


def normalize_cookies(raw_cookies, url):
    """为 cookie 补全 domain 和常用属性"""
    parsed = urlparse(url)
    domain = parsed.hostname

    result = []
    for c in raw_cookies:
        c["domain"] = domain
        c["sameSite"] = "Lax"
        # 同时为关联域名创建副本
        for d in RELAY_DOMAINS:
            if d in c.get("_guess_domain", domain):
                copy = dict(c)
                copy["domain"] = "." + d if not d.startswith(".") else d
                result.append(copy)
        result.append(c)
    return result


def load_credentials(args):
    """加载凭据：命令行参数 > 环境变量 > config.json"""
    user = args.username or os.environ.get("RELAY_USERNAME")
    pwd  = args.password or os.environ.get("RELAY_PASSWORD")
    if not user or not pwd:
        config_path = Path(__file__).parent.parent / "config.json"
        if config_path.exists():
            cfg = json.loads(config_path.read_text(encoding="utf-8"))
            user = user or cfg.get("username")
            pwd  = pwd  or cfg.get("password")
    return user, pwd


# ────────────────────────────── 维普下载 ──────────────────────────────

def download_vip_pdf(page, article_url, output_path):
    """在已登录维普的 page 中，导航到文章阅读页，触发并自动保存 PDF"""
    print(f"[维普] 打开文章: {article_url}")
    page.goto(article_url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)

    # 确保 PDF viewer 加载完成
    try:
        page.wait_for_selector('button:has-text("下载")', timeout=10000)
    except:
        print("[维普] 等待下载按钮超时，尝试继续...")

    download_obj = None

    def on_download(download):
        nonlocal download_obj
        download_obj = download
        print(f"[维普] 捕获下载: {download.suggested_filename}")

    page.on("download", on_download)

    # 方法1: 点击下载按钮
    btn = page.locator('button:has-text("下载")').first
    if btn.count() > 0:
        btn.click()
        page.wait_for_timeout(3000)

    # 方法2: 如果按钮点击无效，通过 pdf.js API 获取数据并用 JS 触发下载
    if not download_obj:
        print("[维普] 按钮未触发下载，尝试 pdf.js 数据导出...")
        try:
            data_b64 = page.evaluate("""async () => {
                const app = window.PDFViewerApplication;
                if (!app || !app.pdfDocument) return null;
                const data = await app.pdfDocument.getData();
                const bytes = new Uint8Array(data);
                let binary = '';
                for (let i = 0; i < bytes.length; i += 8192) {
                    binary += String.fromCharCode.apply(null, bytes.slice(i, i + 8192));
                }
                return btoa(binary);
            }""")
            if data_b64:
                import base64
                pdf_bytes = base64.b64decode(data_b64)
                Path(output_path).write_bytes(pdf_bytes)
                print(f"[维普] pdf.js 导出成功: {output_path} ({len(pdf_bytes)} bytes)")
                return True
        except Exception as e:
            print(f"[维普] pdf.js 导出失败: {e}")

    # 如果捕获了下载事件
    if download_obj:
        download_obj.save_as(output_path)
        print(f"[维普] 下载完成: {output_path}")
        return True

    print("[维普] 所有方法均失败")
    return False


# ────────────────────────────── 知网下载 ──────────────────────────────

def download_cnki_caj(page, article_url, output_path):
    """在已登录知网代理的 page 中，触发 CAJ 下载并自动保存"""
    print(f"[知网] 打开文章: {article_url}")
    page.goto(article_url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(2000)

    download_obj = None

    def on_download(download):
        nonlocal download_obj
        download_obj = download
        print(f"[知网] 捕获下载: {download.suggested_filename}")

    page.on("download", on_download)

    # 点击"下载CAJ格式"链接
    caj_btn = page.locator('a:has-text("下载CAJ格式")').first
    if caj_btn.count() > 0:
        caj_btn.click()
        page.wait_for_timeout(5000)

    if download_obj:
        download_obj.save_as(output_path)
        print(f"[知网] 下载完成: {output_path}")
        return True

    print("[知网] 未捕获到下载事件")
    return False


# ────────────────────────────── 主入口 ──────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="维普/知网 PDF/CAJ 自动下载工具")
    parser.add_argument("--url", required=True, help="文章 URL")
    parser.add_argument("--output", required=True, help="输出文件路径")
    parser.add_argument("--cookie", help="document.cookie 字符串（跳过登录）")
    parser.add_argument("--username", help="中转平台用户名")
    parser.add_argument("--password", help="中转平台密码")
    parser.add_argument("--source", choices=["vip", "cnki"], default="vip",
                        help="来源平台：vip=维普 cnki=知网")
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            # === cookie 复用模式 ===
            if args.cookie:
                print("[Cookie] 解析 cookie 字符串...")
                cookies = parse_cookie_string(args.cookie)

                # 先导航到目标域让 Playwright 建立域名上下文
                parsed = urlparse(args.url)
                base_url = f"{parsed.scheme}://{parsed.hostname}"
                page.goto(base_url, wait_until="domcontentloaded", timeout=15000)

                # 注入 cookie
                try:
                    context.add_cookies(cookies)
                    print(f"[Cookie] 已注入 {len(cookies)} 条 cookie")
                except Exception as e:
                    print(f"[Cookie] 注入警告: {e}")

                # 刷新以应用 cookie
                page.reload(wait_until="networkidle")
                page.wait_for_timeout(1000)

                # 验证登录态
                content = page.content()
                if "维普期刊" in content or "cnki" in page.url.lower():
                    print("[Cookie] 登录态有效")
                else:
                    print("[Cookie] 登录态可能已过期，尝试继续...")

                # 执行下载
                if args.source == "vip":
                    success = download_vip_pdf(page, args.url, args.output)
                else:
                    success = download_cnki_caj(page, args.url, args.output)

                if success:
                    print(f"\n✅ 下载完成: {args.output}")
                else:
                    print("\n❌ 下载失败")
                    sys.exit(1)

            # === 完整登录模式 ===
            else:
                username, password = load_credentials(args)
                if not username or not password:
                    print("错误: 未提供凭据。使用 --cookie 或 --username/--password")
                    sys.exit(1)

                print("[登录] 开始完整登录流程（可能需要验证码）...")
                # 此处调用原有登录函数（如需可补全）
                print("[登录] 完整登录模式暂未实现，请使用 --cookie 模式")
                sys.exit(1)

        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
