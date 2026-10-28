#!/usr/bin/env python3
"""reconcile-drafts.py — 公众号草稿箱与本地 marker 对账。

批量对照远端草稿（Media ID / 标题）与本地文章目录的
.wechat-draft-media-id* marker，输出每篇的一致状态。

安全边界：
- 只读远端（token + draft/batchget），绝不调用 draft/add、draft/update、
  draft/delete，也绝不发消息。
- 默认 --dry-run 只报告；--apply 仅做一种写入：目录没有任何 marker、
  且远端恰好只有一篇标题唯一匹配时，补写 .wechat-draft-media-id。
- 缺失（无 marker 且远端无匹配）、重复（远端同名多篇）、过期
  （marker 的 Media ID 已不在远端）都只报告，不自动处理。

用法：
    python3 reconcile-drafts.py                      # dry-run，全部文章目录
    python3 reconcile-drafts.py --apply              # 唯一匹配时补 marker
    python3 reconcile-drafts.py --dir linux-rcu      # 只看一个目录
    python3 reconcile-drafts.py --env-file /path/.env

退出码：0 = 全部 OK 或仅 MISSING（从未发布过，属正常）；
1 = 存在 STALE / TITLE-MISMATCH / DUPLICATE 等需要人工看的不一致。
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ARTICLES_ROOT = Path.home() / ".siada-cli" / "workspace" / "articles"
MARKER_RE = re.compile(r"^\.wechat-draft-media-id(-v\d+)?$")
API = "https://api.weixin.qq.com/cgi-bin"


def load_env(env_file: Path) -> dict:
    env = {}
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def http_json(url: str, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def get_access_token(app_id: str, app_secret: str) -> str:
    d = http_json(f"{API}/token?grant_type=client_credential&appid={app_id}&secret={app_secret}")
    if "access_token" not in d:
        raise SystemExit(f"取 access_token 失败: errcode={d.get('errcode')} errmsg={d.get('errmsg')}")
    return d["access_token"]


def list_drafts(token: str) -> dict:
    """返回 {media_id: title}，分页拉全。"""
    drafts = {}
    offset = 0
    while True:
        d = http_json(
            f"{API}/draft/batchget?access_token={token}",
            {"offset": offset, "count": 20, "no_content": 0},
        )
        if d.get("errcode"):
            raise SystemExit(f"draft/batchget 失败: errcode={d.get('errcode')} errmsg={d.get('errmsg')}")
        for item in d.get("item", []):
            media_id = item.get("media_id", "")
            content = item.get("content") or {}
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    content = {}
            news = content.get("news_item") or [{}]
            title = (news[0].get("title") or "").strip()
            if media_id:
                drafts[media_id] = title
        total = int(d.get("total_count", 0))
        offset += 20
        if offset >= total or not d.get("item"):
            break
    return drafts


def article_title(md_path: Path):
    text = md_path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^title:\s*(.+?)\s*$", text, re.M)
    if m:
        return m.group(1).strip().strip('"')
    m = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    return m.group(1).strip() if m else None


def marker_version(name: str) -> int:
    m = re.search(r"-v(\d+)$", name)
    return int(m.group(1)) if m else 0


def reconcile_one(root: Path, drafts: dict, apply: bool):
    """返回 (status, detail)。status ∈ OK/STALE/MISMATCH/DUP/MISSING/NO-MARKER/UNVERIFIED"""
    markers = sorted(
        (p for p in root.iterdir() if MARKER_RE.match(p.name)),
        key=lambda p: marker_version(p.name),
    )
    title = article_title(root / "article.md") if (root / "article.md").exists() else None

    if not markers:
        # 唯一标题匹配才补 marker；否则只报告
        matches = [mid for mid, t in drafts.items() if title and t == title]
        if not title:
            return "NO-MARKER", "无 marker，且 article.md 缺标题，跳过"
        if len(matches) == 1:
            if apply:
                (root / ".wechat-draft-media-id").write_text(matches[0] + "\n", encoding="utf-8")
                return "APPLIED", f"补写 marker ← 远端唯一匹配 {matches[0][:12]}…"
            return "NO-MARKER", f"无 marker；远端有唯一同名草稿（--apply 可补）"
        if len(matches) > 1:
            return "DUP", f"无 marker，且远端同名草稿 {len(matches)} 篇，需人工确认"
        return "NO-MARKER", "无 marker，远端也无同名草稿（可能从未发布）"

    # 有 marker：逐个核验最新的一个即可代表当前版本；旧版本 marker 允许已不在远端
    latest = markers[-1]
    media_id = latest.read_text(encoding="utf-8").strip()
    if not media_id:
        return "STALE", f"{latest.name} 内容为空"
    if media_id not in drafts:
        return "STALE", f"{latest.name} 的 Media ID 不在远端草稿箱"
    if title and drafts[media_id] != title:
        return "MISMATCH", f"远端标题「{drafts[media_id]}」≠ 本地「{title}」"
    dup = [m for m, t in drafts.items() if title and t == title and m != media_id]
    if dup:
        return "DUP", f"当前 marker OK，但远端另有 {len(dup)} 篇同名草稿（旧版残留？）"
    return "OK", f"{latest.name} 与远端一致"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(ARTICLES_ROOT), help="文章根目录")
    ap.add_argument("--dir", help="只检查根目录下的这一个子目录")
    ap.add_argument("--env-file", help=".env 路径（默认 根目录/.env，缺失回退各文章目录/.env）")
    ap.add_argument("--apply", action="store_true", help="允许为唯一匹配的无 marker 目录补写 marker")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    args = ap.parse_args()

    root = Path(args.root).expanduser()
    env_file = Path(args.env_file) if args.env_file else None
    if env_file is None:
        candidates = [root / ".env"] + sorted(root.glob("*/.env"), key=lambda p: p.stat().st_mtime, reverse=True)
        env_file = next((p for p in candidates if p.exists() and "WECHAT_APP_ID" in p.read_text(errors="replace")), None)
    if env_file is None:
        raise SystemExit("找不到含 WECHAT_APP_ID 的 .env")
    env = load_env(env_file)
    if not env.get("WECHAT_APP_ID") or not env.get("WECHAT_APP_SECRET"):
        raise SystemExit(".env 缺少 WECHAT_APP_ID / WECHAT_APP_SECRET")

    token = get_access_token(env["WECHAT_APP_ID"], env["WECHAT_APP_SECRET"])
    drafts = list_drafts(token)

    dirs = [root / args.dir] if args.dir else sorted(p for p in root.iterdir() if (p / "article.md").exists())
    results = {}
    bad = 0
    for d in dirs:
        if not (d / "article.md").exists():
            continue
        status, detail = reconcile_one(d, drafts, args.apply)
        results[d.name] = {"status": status, "detail": detail}
        if status in ("STALE", "MISMATCH", "DUP"):
            bad += 1

    if args.json:
        print(json.dumps({"remote_drafts": len(drafts), "articles": results}, ensure_ascii=False, indent=2))
    else:
        icon = {"OK": "✅", "APPLIED": "", "NO-MARKER": "ℹ️ ", "STALE": "⚠️", "MISMATCH": "❌", "DUP": "❌"}
        print(f"远端草稿 {len(drafts)} 篇；本地检查 {len(results)} 个目录（模式: {'apply' if args.apply else 'dry-run'}）\n")
        for name in sorted(results, key=lambda n: (results[n]["status"] == "OK", n)):
            r = results[name]
            print(f"{icon.get(r['status'], '•')} [{r['status']:>8}] {name}: {r['detail']}")
        print(f"\n汇总: OK={sum(1 for r in results.values() if r['status']=='OK')} "
              f"NO-MARKER={sum(1 for r in results.values() if r['status']=='NO-MARKER')} "
              f"APPLIED={sum(1 for r in results.values() if r['status']=='APPLIED')} "
              f"需人工={bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
