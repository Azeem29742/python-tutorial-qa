"""Download every chapter linked from the official Python Tutorial index."""
import json
import re
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from app.core.config import CORPUS_PATH, DOCS_INDEX_URL


def clean_title(heading) -> str:
    title = " ".join(heading.get_text(" ", strip=True).replace("¶", "").split())
    return re.sub(r"^\d+(?:\.\d+)*\.\s*", "", title).strip()


def section_record(section, page_url):
    heading = section.find(["h1", "h2", "h3", "h4"], recursive=False)
    if heading is None:
        heading = section.find(["h1", "h2", "h3", "h4"])
    if heading is None:
        return None
    title = clean_title(heading)
    if not title:
        return None
    anchor = section.get("id") or heading.get("id")
    parts = []
    for node in section.find_all(["p", "pre", "li"]):
        if node.find_parent("section") is section:
            value = " ".join(node.get_text(" ", strip=True).split())
            if value:
                parts.append(value)
    if not parts:
        return None
    return {"section": title, "anchor": anchor or "",
            "url": page_url + ("#" + anchor if anchor else ""), "text": " ".join(parts)}


def main() -> None:
    session = requests.Session()
    response = session.get(DOCS_INDEX_URL, timeout=45)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    index = BeautifulSoup(response.text, "html.parser")
    root = index.select_one("div[role=main]") or index.select_one("div.body")
    if root is None:
        raise RuntimeError("Could not locate tutorial contents on official docs index")
    chapter_urls = set()
    for link in root.select("a[href]"):
        url = urljoin(DOCS_INDEX_URL, link["href"]).split("#", 1)[0]
        path = urlparse(url).path
        if "/tutorial/" in path and path.endswith(".html") and not path.endswith("/index.html"):
            chapter_urls.add(url)
    if not chapter_urls:
        raise RuntimeError("No tutorial chapter links found on the official index")
    records = []
    for page_url in sorted(chapter_urls):
        page = session.get(page_url, timeout=45)
        page.raise_for_status()
        page.encoding = page.apparent_encoding
        soup = BeautifulSoup(page.text, "html.parser")
        main_content = soup.select_one("div[role=main]") or soup.select_one("div.body")
        if main_content is None:
            continue
        sections = main_content.select("section")
        for section in sections:
            record = section_record(section, page_url)
            if record:
                records.append(record)
    if not records:
        raise RuntimeError("No tutorial sections extracted; docs HTML structure may have changed")
    CORPUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CORPUS_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(records)} sections from {len(chapter_urls)} official tutorial pages to {CORPUS_PATH}")


if __name__ == "__main__":
    main()
