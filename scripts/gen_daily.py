#!/usr/bin/env python3
"""自动生成技术日报 — 抓取 GitHub Trending + Hacker News"""

import json
import re
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "src" / "content" / "posts"

HEADERS = {"User-Agent": "Mozilla/5.0 (tech-daily-bot/1.0)"}


def fetch_json(url: str, timeout: int = 15) -> dict | list:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def fetch_text(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


# ─── GitHub Trending ─────────────────────────────────────────────

def get_github_trending() -> list[dict]:
    """通过 GitHub API 获取近期高星项目"""
    repos = []

    # 查询近 3 天创建的高星项目
    since = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    url = (
        f"https://api.github.com/search/repositories"
        f"?q=created:>{since}+stars:>50&sort=stars&order=desc&per_page=15"
    )
    try:
        data = fetch_json(url)
        for r in data.get("items", [])[:10]:
            desc = (r.get("description") or "")[:150]
            # 过滤 spam 项目
            if _is_spam(desc):
                continue
            repos.append({
                "name": r["full_name"],
                "url": r["html_url"],
                "desc": desc,
                "stars": r["stargazers_count"],
                "lang": r.get("language") or "",
            })
    except Exception as e:
        print(f"  GitHub API 错误: {e}")

    # 如果结果太少，补充高星活跃项目
    if len(repos) < 5:
        url2 = (
            "https://api.github.com/search/repositories"
            "?q=stars:>1000+pushed:>2026-05-20&sort=stars&order=desc&per_page=8"
        )
        try:
            data2 = fetch_json(url2)
            existing = {r["name"] for r in repos}
            for r in data2.get("items", [])[:8]:
                if r["full_name"] in existing:
                    continue
                repos.append({
                    "name": r["full_name"],
                    "url": r["html_url"],
                    "desc": (r.get("description") or "")[:150],
                    "stars": r["stargazers_count"],
                    "lang": r.get("language") or "",
                })
        except Exception as e:
            print(f"  GitHub 补充查询错误: {e}")

    return repos[:8]


def _is_spam(desc: str) -> bool:
    """检测 spam 项目描述"""
    lower = desc.lower()
    spam_signals = ["trading bot", "copy trading", "arbitrage bot"]
    # 重复词超过 3 次视为 spam
    words = lower.split()
    if len(words) > 10:
        from collections import Counter
        most_common = Counter(words).most_common(1)[0][1]
        if most_common > 3:
            return True
    return any(s in lower for s in spam_signals)


# ─── Hacker News ─────────────────────────────────────────────────

def get_hn_top(count: int = 6) -> list[dict]:
    """获取 HN 热门故事"""
    stories = []
    try:
        ids = fetch_json(
            "https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10
        )[:20]

        for sid in ids:
            if len(stories) >= count:
                break
            try:
                item = fetch_json(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    timeout=5,
                )
                title = item.get("title", "")
                url = item.get("url", f"https://news.ycombinator.com/item?id={sid}")
                score = item.get("score", 0)
                if score < 50:
                    continue
                stories.append({
                    "title": title,
                    "url": url,
                    "score": score,
                })
            except Exception:
                continue
    except Exception as e:
        print(f"  HN API 错误: {e}")

    return stories


# ─── 生成 Markdown ──────────────────────────────────────────────

def _stars_label(n: int) -> str:
    if n >= 1000:
        return f"{n/1000:.1f}K+"
    return f"{n}+"


def _lang_tag(lang: str) -> str:
    tags = {
        "TypeScript": "前端",
        "JavaScript": "前端",
        "Python": "Python",
        "Rust": "Rust",
        "Go": "Go",
        "C++": "C++",
        "C": "系统编程",
        "Java": "Java",
    }
    return tags.get(lang, lang) if lang else "开源"


def generate_markdown(date_str: str, repos: list[dict], hn: list[dict]) -> str:
    lines = [
        "---",
        f'title: "技术日报 · {date_str.replace("-", ".")}"',
        'description: "GitHub 热门项目速览 + 技术圈每日动态。"',
        f"pubDate: {date_str}",
        'category: "日报"',
        'tags: ["GitHub", "日报", "AI", "开源"]',
        "featured: false",
        "---",
        "",
        "> 每日精选：GitHub 热门项目 + 技术圈新鲜事。",
        "",
        "## GitHub 热门",
        "",
    ]

    for r in repos[:6]:
        stars = _stars_label(r["stars"])
        tag = _lang_tag(r["lang"])
        lines.append(f"### [{r['name']}]({r['url']})")
        lines.append("")
        lines.append(f"> {r['desc']}")
        lines.append(f"> 📝 {tag}")
        lines.append("")
        lines.append(f"⭐ {stars} stars")
        lines.append("")

    # AI/LLM 专区
    ai_repos = [r for r in repos if any(
        k in (r["desc"] + r["name"]).lower()
        for k in ["ai", "llm", "agent", "gpt", "claude", "model"]
    )]
    if ai_repos:
        lines.append("## AI/LLM 动态")
        lines.append("")
        for r in ai_repos[:3]:
            stars = _stars_label(r["stars"])
            lines.append(f"### [{r['name']}]({r['url']})")
            lines.append("")
            lines.append(f"> {r['desc']}")
            lines.append(f"> 📝 AI · {_lang_tag(r['lang'])}")
            lines.append("")
            lines.append(f"⭐ {stars} stars")
            lines.append("")

    # HN
    if hn:
        lines.append("## Hacker News 热门")
        lines.append("")
        for s in hn:
            lines.append(f"### [{s['title']}]({s['url']})")
            lines.append("")
            lines.append(f"> {s['score']} 分 · {s['title']}")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("> 数据来源：GitHub API · Hacker News Firebase API")

    return "\n".join(lines)


# ─── 主流程 ─────────────────────────────────────────────────────

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = CONTENT_DIR / f"daily-tech-{today}.md"

    if filepath.exists():
        print(f"日报已存在: {filepath.name}")
        return

    print(f"生成 {today} 技术日报...")

    print("  [1/2] 抓取 GitHub Trending...")
    repos = get_github_trending()
    print(f"        获取 {len(repos)} 个项目")

    print("  [2/2] 抓取 Hacker News...")
    hn = get_hn_top(6)
    print(f"        获取 {len(hn)} 条新闻")

    md = generate_markdown(today, repos, hn)
    filepath.write_text(md, encoding="utf-8")
    print(f"\n已生成: {filepath}")


if __name__ == "__main__":
    main()
