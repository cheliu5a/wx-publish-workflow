#!/usr/bin/env node
/**
 * publish-wx-html.mjs
 * 将 wx-article 生成的内联样式 HTML 直接发布到微信公众号草稿箱
 *
 * 用法：
 *   node publish-wx-html.mjs --html article_wx.html --title "标题" [--cover cover.jpg] [--author 作者]
 *
 * 环境变量（从 .env 读取）：
 *   WECHAT_APP_ID
 *   WECHAT_APP_SECRET
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

// 读取 .env（从当前工作目录）
const dotenvPath = path.join(process.cwd(), ".env");
if (fs.existsSync(dotenvPath)) {
  const lines = fs.readFileSync(dotenvPath, "utf-8").split("\n");
  for (const line of lines) {
    const m = line.match(/^\s*([A-Z_]+)\s*=\s*(.+)\s*$/);
    if (m) process.env[m[1]] = m[2].trim();
  }
}

// 解析命令行参数
const args = process.argv.slice(2);
const get = (flag) => {
  const i = args.indexOf(flag);
  return i !== -1 ? args[i + 1] : null;
};

const htmlFile = get("--html");
const title = get("--title");
const cover = get("--cover");
const author = get("--author") || "";

if (!htmlFile || !title) {
  console.error("用法: node publish-wx-html.mjs --html <file> --title <title> [--cover <img>] [--author <name>]");
  process.exit(1);
}

// 读取 HTML 内容（wx-article 生成的带内联样式 HTML）
const htmlContent = fs.readFileSync(path.resolve(process.cwd(), htmlFile), "utf-8");

// 提取 <body> 内容（微信只需要正文 HTML，不需要 <html>/<head>）
let content = htmlContent;
const bodyMatch = htmlContent.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
if (bodyMatch) {
  content = bodyMatch[1].trim();
}

// 调用 publishToWechatDraft
const WENYAN_CORE = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  "../../feishu-wechat-cli/node_modules/.pnpm/@wenyan-md+core@2.0.8_form-data-encoder@4.1.0_formdata-node@6.0.3_jsdom@27.4.0/node_modules/@wenyan-md/core/dist/publish.js"
);

const { publishToWechatDraft } = await import(WENYAN_CORE);

const coverPath = cover ? path.resolve(process.cwd(), cover) : undefined;

try {
  const result = await publishToWechatDraft({
    title,
    content,
    cover: coverPath,
    author,
  });

  if (result.media_id) {
    console.log(`发布成功，Media ID: ${result.media_id}`);
  } else {
    console.error("发布失败:", JSON.stringify(result));
    process.exit(1);
  }
} catch (e) {
  console.error("发布出错:", e.message || e);
  process.exit(1);
}
