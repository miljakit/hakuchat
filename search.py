import subprocess
import urllib.parse
import re
import sys
import gzip
import io


def web_search(query: str, max_results: int = 5) -> list[dict]:
    encoded_query = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

    cmd = [
        "curl",
        "-s",
        "-L",
        "-A",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-H",
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "-H",
        "Accept-Language: en-US,en;q=0.9",
        "-H",
        "Accept-Encoding: gzip, deflate, br",
        "-H",
        "DNT: 1",
        "-H",
        "Connection: keep-alive",
        "-H",
        "Upgrade-Insecure-Requests: 1",
        "--compressed",
        "--max-time",
        "10",
        url,
    ]

    result = subprocess.run(cmd, capture_output=True, timeout=15)

    if result.returncode != 0:
        return []

    html = result.stdout
    if html.startswith(b"\x1f\x8b"):
        html = gzip.decompress(html)
    html = html.decode("utf-8", errors="replace")

    snippet_pattern = r'<a class="result__snippet"[^>]*href="([^"]*)"[^>]*>(.*?)</a>'
    matches = re.findall(snippet_pattern, html, re.DOTALL)

    results = []
    for href, text in matches[:max_results]:
        clean_text = re.sub(r"<[^>]+>", "", text).strip()
        clean_text = re.sub(r"\s+", " ", clean_text)
        if clean_text:
            full_url = href
            if href.startswith("//"):
                full_url = "https:" + href
            elif href.startswith("/"):
                full_url = "https://duckduckgo.com" + href
            results.append({"title": clean_text, "url": full_url})

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search.py \"search query\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    results = web_search(query)

    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}")
        if r["url"]:
            print(f"   {r['url']}")
        print()