#!/usr/bin/env python3
"""preflight.py — feishu-wechat publish 前的发布门槛检查。

在文章目录下运行：python3 preflight.py [article_dir]

检查项（任一失败即退出码 1，不得进入 publish）：
1. 主封面 article-cover.png 必须为 2100x900
2. 方形封面 article-cover-square.png 必须为 1080x1080
3. article.md 中所有本地图片引用 ![alt](path) 文件必须存在
4. article.md 不得残留归档占位符「> 📷 图：」

封面尺寸不合格时当场重生成，不要让不合格封面流入 publish 环节。

开工检查模式：python3 preflight.py --kickoff [article_dir]
写稿/配图前一次性报出凭据与工具缺失，不留到封面/发布环节才发现：
1. 文章目录 .env（WECHAT_APP_ID/SECRET）——缺失时自动从兄弟文章目录复制最新一份并置 600
2. LABNANA_API_KEY（环境变量或任一 .labnana.env）——仅告警，缺失时降级走矢量封面
3. wx-publish-workflow 权威目录与 agent-workspace 镜像副本的哈希比对——不一致仅告警，需显式同步
4. node playwright 可用性
"""
import glob
import hashlib
import os
import re
import shutil
import stat
import subprocess
import sys

REQUIRED = [("article-cover.png", 2100, 900),
            ("article-cover-square.png", 1080, 1080)]

ARTICLES_ROOT = os.path.expanduser("~/.siada-cli/workspace/articles")
LABNANA_SEARCH = [os.path.expanduser("~/.agents/skills"),
                  os.path.expanduser("~/.siada-cli/workspace")]

# wx-publish-workflow 唯一权威源与镜像副本（用于 kickoff 漂移提示）
SKILL_AUTHORITATIVE = os.path.expanduser("~/.siada-cli/skills/content/wx-publish-workflow")
SKILL_MIRROR = os.path.expanduser("~/.siada-cli/workspace/agent-workspace/skills/wx-publish-workflow")
SKIP_DIRS = {"__pycache__", ".git", ".pytest_cache"}


def _hash_dir(root):
    files = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            try:
                with open(full, "rb") as f:
                    files[rel] = hashlib.sha256(f.read()).hexdigest()
            except OSError:
                files[rel] = None
    return files


def check_skill_drift():
    """比对权威目录与镜像副本；镜像不存在时返回 None（跳过）。"""
    if not os.path.isdir(SKILL_MIRROR):
        return None
    a, b = _hash_dir(SKILL_AUTHORITATIVE), _hash_dir(SKILL_MIRROR)
    stale = sorted(k for k in a if k in b and a[k] != b[k])
    missing = sorted(k for k in a if k not in b)
    extra = sorted(k for k in b if k not in a)
    return stale, missing, extra


def kickoff(d):
    errors, warnings = [], []

    env_path = os.path.join(d, ".env")
    if not (os.path.isfile(env_path)
            and "WECHAT_APP_ID" in open(env_path, encoding="utf-8").read()):
        siblings = sorted((p for p in glob.glob(os.path.join(ARTICLES_ROOT, "*", ".env"))
                           if os.path.abspath(p) != env_path
                           and "WECHAT_APP_ID" in open(p, encoding="utf-8").read()),
                          key=os.path.getmtime, reverse=True)
        if siblings:
            shutil.copyfile(siblings[0], env_path)
            os.chmod(env_path, stat.S_IRUSR | stat.S_IWUSR)
            print(f".env 已从兄弟目录复制：{siblings[0]}（权限 600）")
        else:
            errors.append(f"缺 {env_path}（WECHAT_APP_ID/SECRET），且无兄弟目录 .env 可复制")

    if not os.environ.get("LABNANA_API_KEY"):
        found = False
        for root in LABNANA_SEARCH:
            for p in glob.glob(os.path.join(root, "**", ".labnana.env"), recursive=True):
                if "LABNANA_API_KEY" in open(p, encoding="utf-8",
                                             errors="ignore").read():
                    found = True
                    break
            if found:
                break
        if not found:
            warnings.append("未找到 LABNANA_API_KEY（env 或 .labnana.env），封面将降级为矢量方案")

    drift = check_skill_drift()
    if drift:
        stale, missing, extra = drift
        if stale or missing or extra:
            lines = ["wx-publish-workflow 镜像副本与权威目录不一致（权威：~/.siada-cli/skills/content/wx-publish-workflow/）："]
            if stale:
                lines.append(f"  内容过期 {len(stale)}: " + ", ".join(stale[:5]) + (" …" if len(stale) > 5 else ""))
            if missing:
                lines.append(f"  镜像缺失 {len(missing)}: " + ", ".join(missing[:5]) + (" …" if len(missing) > 5 else ""))
            if extra:
                lines.append(f"  镜像多余 {len(extra)}: " + ", ".join(extra[:5]) + (" …" if len(extra) > 5 else ""))
            lines.append("  如需同步请显式复制文件（cp -r），勿使用 symlink。")
            warnings.append("\n".join(lines))

    try:
        subprocess.run(["npx", "--no-install", "playwright", "--version"],
                       capture_output=True, check=True, timeout=15)
    except Exception:
        errors.append("node playwright 不可用（npx --no-install playwright --version 失败）")

    for w in warnings:
        print(f"WARN: {w}")
    if errors:
        print("kickoff 检查未通过：")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("kickoff 检查通过")



def main():
    args = sys.argv[1:]
    if args and args[0] == "--kickoff":
        d = os.path.abspath(args[1]) if len(args) > 1 else os.getcwd()
        kickoff(d)
        return
    d = os.path.abspath(args[0]) if args else os.getcwd()
    errors = []

    try:
        from PIL import Image
    except ImportError:
        sys.exit("缺少 PIL：pip3 install Pillow")

    for name, w, h in REQUIRED:
        p = os.path.join(d, name)
        if not os.path.isfile(p):
            errors.append(f"缺封面 {name}")
            continue
        with Image.open(p) as im:
            if im.size != (w, h):
                errors.append(f"{name} 尺寸 {im.size[0]}x{im.size[1]}，要求 {w}x{h}")

    md = os.path.join(d, "article.md")
    text = open(md, encoding="utf-8").read()
    for alt, path in re.findall(r"!\[([^\]]*)\]\(([^)\s]+)\)", text):
        if path.startswith("http"):
            continue
        if not os.path.isfile(os.path.join(d, path)):
            errors.append(f"正文图片不存在：{path}（{alt}）")
    if "> 📷 图：" in text:
        errors.append("article.md 残留归档占位符「> 📷 图：」，应为真实图片引用")

    if errors:
        print("preflight 未通过：")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("preflight 通过")


if __name__ == "__main__":
    main()
