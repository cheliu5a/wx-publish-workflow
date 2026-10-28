#!/usr/bin/env python3
"""sync-series.py — 同步「Linux 延迟」系列回顾表到所有已发布文章。

权威来源：articles/planforlinux.md 的「## 已发布」段
（篇号、标题、公众号文章链接、本地文件均从这里读；新增发布后先补 planforlinux）。
系列回顾是读者可见内容，链接只允许公众号文章 URL（mp.weixin.qq.com）；
没有公众号链接时显示纯标题，不能回退使用飞书文档链接。

「核心反直觉点」列来自各篇新格式系列表的现有行（按飞书链接匹配；
某篇自己的行取它表里标注（本文）的那行）。

只处理新格式表（含「核心反直觉点」列、篇号 ①/深水区① 的文章；
旧格式表（mp.weixin 链接、一二三编号）跳过并提示，不强行改写。

用法：
  python3 sync-series.py                # dry-run
  python3 sync-series.py --apply        # 写回 article.md
  python3 sync-series.py --apply --publish
    # 对表格有变化且带 .wechat-draft-media-id* 的文章重跑 feishu-wechat publish，
    # 新 media id 存为下一个 -vN marker（不覆盖旧 marker）
"""
import argparse
import glob
import os
import re
import subprocess
import sys

ARTICLES = os.path.expanduser("~/.siada-cli/workspace/articles")
PLAN = os.path.join(ARTICLES, "planforlinux.md")
ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(?:\[([^\]]+)\]\(([^)]+)\)|([^|]+?))\s*\|\s*([^|]+?)\s*\|$")
SECTION_RE = re.compile(r"(## 系列回顾\n\n\|[^\n]*核心反直觉点[^\n]*\n\|[-|\s]+\n)((?:\|[^\n]+\n)+)")


def parse_plan():
    """解析 planforlinux.md 已发布段 → [(label, title, url, local_dir)]"""
    text = open(PLAN, encoding="utf-8").read()
    sec = re.search(r"## 已发布\n(.*?)\n---", text, re.DOTALL)
    entries = []
    series = None
    for line in sec.group(1).split("\n"):
        m = re.match(r"### (主系列|深水区)", line)
        if m:
            series = m.group(1)
            continue
        m = re.match(r"#### ([①-⑳]) (.+)", line)
        if m:
            label = m.group(1) if series == "主系列" else f"深水区{m.group(1)}"
            entries.append({"label": label, "heading": m.group(2).strip()})
            continue
        if not entries:
            continue
        e = entries[-1]
        m = re.match(r"- 标题：(.+)", line)
        if m and not e.get("title"):
            e["title"] = m.group(1).strip()
        m = re.match(r"- 公众号文章：(https?://\S+)", line)
        if m:
            url = m.group(1).strip()
            if "mp.weixin.qq.com" in url:
                e["url"] = url
        m = re.match(r"- 本地文件：`([^/`]+)", line)
        if m:
            e["dir"] = m.group(1).strip()
    out = []
    for e in entries:
        if not e.get("title") and e.get("heading"):
            # 标题回退：取 heading 中「：」后的部分（公众号标题习惯放冒号后）
            h = e["heading"]
            e["title"] = h.split("：", 1)[-1].strip() if "：" in h else h
        if e.get("title") and e.get("dir"):
            out.append(e)
    return out


def _norm(s):
    return re.sub(r"[\s`\"'“”‘’（）()【】《》：:，,。.？?！!、/]", "", s or "")


def _title_match(a, b):
    a, b = _norm(a), _norm(b)
    if not a or not b:
        return False
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i >= 12 or a in b or b in a


def parse_table(text):
    """新格式表 → (rows by url-or-self, self_url_guess)"""
    m = SECTION_RE.search(text)
    if not m:
        return None
    rows = []
    for line in m.group(2).strip().split("\n"):
        rm = ROW_RE.match(line.strip())
        if not rm:
            continue
        title = (rm.group(2) or rm.group(4) or "").strip()
        is_self = "本文" in title
        title = re.sub(r"[（(]本文[)）]", "", title).strip()
        rows.append({"title": title, "url": (rm.group(3) or "").strip(),
                     "point": rm.group(5).strip(), "self": is_self})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()

    entries = parse_plan()
    by_dir = {e["dir"]: e for e in entries}

    # 收集各篇文章的新格式表
    arts = {}
    for d in sorted(glob.glob(os.path.join(ARTICLES, "*/"))):
        name = os.path.basename(d.rstrip("/"))
        f = os.path.join(d, "article.md")
        if not os.path.isfile(f):
            continue
        text = open(f, encoding="utf-8").read()
        if "## 系列回顾" not in text:
            continue
        rows = parse_table(text)
        if rows is None:
            print(f"[skip] {name}：旧格式系列表，不在同步范围")
            continue
        arts[name] = {"dir": d, "file": f, "text": text, "rows": rows}

    # 反直觉点：优先取该篇自己表里的（本文）行；否则取任意表按 url 匹配的行
    for e in entries:
        self_rows = arts.get(e["dir"], {}).get("rows", [])
        for r in self_rows:
            if r["self"]:
                e["point"] = r["point"]
                break
        else:
            for a in arts.values():
                for r in a["rows"]:
                    if (e.get("url") and r["url"] == e["url"]) or \
                       _title_match(r["title"], e["title"]):
                        e["point"] = r["point"]
                        break
                if e.get("point"):
                    break
        if not e.get("point"):
            print(f"[warn] {e['label']} {e['title'][:20]} 缺反直觉点，留空")
            e["point"] = ""

    def render(self_dir):
        out = []
        for e in entries:
            if e["dir"] == self_dir:
                out.append(f"| {e['label']} | {e['title']}（本文） | {e['point']} |")
            elif e.get("url") and "mp.weixin.qq.com" in e["url"]:
                out.append(f"| {e['label']} | [{e['title']}]({e['url']}) | {e['point']} |")
            else:
                out.append(f"| {e['label']} | {e['title']} | {e['point']} |")
        return "\n".join(out) + "\n"

    changed = []
    for name, a in arts.items():
        if name not in by_dir:
            print(f"[skip] {name}：不在 planforlinux 已发布清单")
            continue
        new_text = SECTION_RE.sub(lambda m: m.group(1) + render(name), a["text"], count=1)
        if new_text != a["text"]:
            changed.append((name, a))
            print(f"[diff] {name}")
            if args.apply:
                open(a["file"], "w", encoding="utf-8").write(new_text)

    print(f"\n系列共 {len(entries)} 篇；{len(changed)} 篇表格需更新"
          f"{'（已写回）' if args.apply else '（dry-run）'}")

    if args.publish and args.apply:
        # wenyan core 会把 access token 缓存到 ~/.config/wenyan-md/token.json（TTL 7200s），
        # 但 CLI 图片上传每次另取新 token 会使缓存 token 提前失效，TTL 却仍判定有效，
        # 导致后续发布复用死 token 报 40001。每次发布前清缓存强制取新 token。
        token_cache = os.path.expanduser("~/.config/wenyan-md/token.json")
        for name, a in changed:
            d = a["dir"]
            markers = sorted(glob.glob(os.path.join(d, ".wechat-draft-media-id*")))
            if not markers:
                print(f"[skip publish] {name} 无草稿 marker")
                continue
            if os.path.exists(token_cache):
                os.remove(token_cache)
            n = len(markers)
            r = subprocess.run(["feishu-wechat", "publish", "-f", "article.md",
                                "--article-cover", "./article-cover.png"],
                               cwd=d, capture_output=True, text=True)
            out = (r.stdout + r.stderr).strip()
            print(out)
            m = re.search(r"Media ID: ([A-Za-z0-9_\-]+)", out)
            if m:
                open(os.path.join(d, f".wechat-draft-media-id-v{n + 1}"), "w").write(m.group(1))
                open(os.path.join(d, f"publish-output-v{n + 1}.txt"), "w").write(out + "\n")
            else:
                print(f"[FAIL] {name} 发布失败，未写 marker", file=sys.stderr)


if __name__ == "__main__":
    main()
