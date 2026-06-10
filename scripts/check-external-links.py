#!/usr/bin/env python3
"""Check external links in the live Herm Mintlify Markdown exports.

Default behavior is watchdog-friendly: print nothing and exit 0 when all checked
links pass. On failures, print one actionable line per failing URL and exit 1.
"""
from __future__ import annotations

import argparse
import concurrent.futures as futures
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser

DEFAULT_BASE = "https://herm.liftaris.dev"
UA = "Herm docs external-link-check/1.0 (+https://herm.liftaris.dev)"
TIMEOUT = 15

IGNORED_HOSTS = {
    # GitHub can rate-limit HEAD aggressively; the checker falls back to GET.
}

@dataclass(frozen=True)
class LinkRef:
    source: str
    url: str

class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for key, value in attrs:
            if key == "href" and value:
                self.hrefs.append(value)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
        return response.read().decode("utf-8", "replace")


def core_pages(base: str) -> set[str]:
    return {
        f"{base}/introduction.md",
        f"{base}/quickstart.md",
        f"{base}/configuration.md",
        f"{base}/customization/themes.md",
        f"{base}/customization/keybindings.md",
        f"{base}/customization/slash-commands.md",
        f"{base}/troubleshooting/common-issues.md",
        f"{base}/skill.md",
    }


def docs_pages(base: str) -> tuple[list[str], list[str]]:
    pages = core_pages(base)
    failures: list[str] = []
    try:
        llms = fetch_text(f"{base}/llms.txt")
    except Exception as exc:
        failures.append(f"{base}/llms.txt — {type(exc).__name__}: {exc}")
        return sorted(pages), failures

    host = urllib.parse.urlparse(base).netloc
    for url in re.findall(r"https?://[^\s)]+", llms):
        clean = url.rstrip(".,")
        parsed = urllib.parse.urlparse(clean)
        if parsed.netloc != host:
            continue
        if parsed.path.endswith(".md"):
            pages.add(clean)
        elif parsed.path not in {"", "/"}:
            pages.add(urllib.parse.urljoin(base, parsed.path.rstrip("/") + ".md"))
    return sorted(pages), failures


def extract_links(source: str, text: str, base: str) -> list[LinkRef]:
    refs: list[LinkRef] = []
    candidates = set(re.findall(r"https?://[^\s)\]}>\"']+", text))
    candidates.update(re.findall(r"\[[^\]]+\]\((https?://[^)]+)\)", text))
    parser = AnchorParser()
    try:
        parser.feed(text)
        candidates.update(parser.hrefs)
    except Exception:
        pass
    for raw in candidates:
        url = raw.strip().rstrip(".,;:!")
        if not url.startswith(("http://", "https://")):
            continue
        parsed = urllib.parse.urlparse(url)
        if parsed.netloc == urllib.parse.urlparse(base).netloc:
            continue
        if parsed.scheme not in {"http", "https"}:
            continue
        refs.append(LinkRef(source, urllib.parse.urldefrag(url)[0]))
    return refs


def request_status(url: str) -> tuple[bool, str]:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc in IGNORED_HOSTS:
        return True, "ignored"
    ctx = ssl.create_default_context()
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as response:
                status = response.status
                if 200 <= status < 400:
                    return True, f"{status} {method}"
                if method == "HEAD" and status in {405, 403, 429}:
                    continue
                return False, f"HTTP {status} {method}"
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in {405, 403, 429}:
                continue
            if 200 <= exc.code < 400:
                return True, f"{exc.code} {method}"
            return False, f"HTTP {exc.code} {method}"
        except Exception as exc:
            if method == "HEAD":
                continue
            return False, f"{type(exc).__name__}: {exc}"
    return False, "unreachable"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    refs: list[LinkRef] = []
    pages, discovery_failures = docs_pages(args.base.rstrip("/"))
    for page in pages:
        try:
            text = fetch_text(page)
            refs.extend(extract_links(page, text, args.base.rstrip("/")))
        except Exception as exc:
            refs.append(LinkRef(page, f"PAGE_FETCH_FAILED::{type(exc).__name__}: {exc}"))

    by_url: dict[str, set[str]] = {}
    page_failures: list[str] = list(discovery_failures)
    for ref in refs:
        if ref.url.startswith("PAGE_FETCH_FAILED::"):
            page_failures.append(f"{ref.source} — {ref.url.removeprefix('PAGE_FETCH_FAILED::')}")
            continue
        by_url.setdefault(ref.url, set()).add(ref.source)

    failures: list[str] = []
    with futures.ThreadPoolExecutor(max_workers=8) as pool:
        future_map = {pool.submit(request_status, url): url for url in sorted(by_url)}
        for fut in futures.as_completed(future_map):
            url = future_map[fut]
            ok, detail = fut.result()
            if args.verbose:
                print(f"{'ok' if ok else 'fail'} {url} — {detail}")
            if not ok:
                sources = ", ".join(sorted(by_url[url])[:3])
                more = "" if len(by_url[url]) <= 3 else f" (+{len(by_url[url]) - 3} more)"
                failures.append(f"{url} — {detail} — {sources}{more}")

    if page_failures or failures:
        print("Herm docs external link check failed:")
        for line in page_failures:
            print(f"PAGE {line}")
        for line in sorted(failures):
            print(f"LINK {line} — suggested action: update or remove the source link, or document an ignore only for confirmed bot-blocking/transient targets")
        return 1

    if args.verbose:
        print(f"checked {len(by_url)} external links across live Herm docs exports")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
