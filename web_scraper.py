import json
import csv
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Required: requests and beautifulsoup4.")
    print("Install: pip install requests beautifulsoup4")
    raise SystemExit(1)


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def fetch_page(url: str, timeout: int = 30) -> Optional[str]:
    try:
        print(f"Fetching: {url}")
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        print(f"Success ({len(resp.text)} bytes)")
        return resp.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_text(html: str, selector: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.select(selector)
    return [el.get_text(strip=True) for el in elements]


def extract_links(html: str, selector: str, base_url: str = "") -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.select(selector):
        href = a.get("href")
        if href:
            if base_url and href.startswith("/"):
                href = base_url.rstrip("/") + href
            links.append(href)
    return links


def extract_table(html: str, table_selector: str = "table") -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one(table_selector)
    if not table:
        print(f"No table found for selector '{table_selector}'")
        return []
    headers = [th.get_text(strip=True) for th in table.select("thead th, tr:first-child th, tr:first-child td")]
    rows = []
    for tr in table.select("tbody tr, tr:not(:first-child)"):
        cells = [td.get_text(strip=True) for td in tr.select("td")]
        if cells:
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
            else:
                rows.append({f"col_{i}": c for i, c in enumerate(cells)})
    return rows


def extract_images(html: str, selector: str = "img") -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    return [img.get("src", "") for img in soup.select(selector) if img.get("src")]


def scrape_generic(url: str) -> Dict[str, Any]:
    html = fetch_page(url)
    if not html:
        return {"error": "Failed to fetch page"}
    soup = BeautifulSoup(html, "html.parser")
    return {
        "url": url,
        "title": soup.title.string.strip() if soup.title and soup.title.string else "",
        "meta_description": "",
        "headings": {
            "h1": [h.get_text(strip=True) for h in soup.select("h1")],
            "h2": [h.get_text(strip=True) for h in soup.select("h2")],
        },
        "paragraphs": [p.get_text(strip=True) for p in soup.select("p") if p.get_text(strip=True)],
        "links": len(soup.select("a[href]")),
        "images": len(soup.select("img[src]")),
    }


def save_to_json(data: Any, filename: str):
    path = Path(filename)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"Saved: {filename}")


def save_to_csv(data: List[Dict], filename: str):
    if not data:
        print("No data to save.")
        return
    path = Path(filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved: {filename}")


def interactive_scrape():
    url = input("URL to scrape: ").strip()
    if not url:
        print("No URL provided.")
        return
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    print("\nSelect scrape type:")
    print("  [1] Generic (title, headings, paragraphs, links)")
    print("  [2] Extract text by CSS selector")
    print("  [3] Extract links by CSS selector")
    print("  [4] Extract table data")
    print("  [5] Extract all images")
    choice = input("\nChoice (1-5): ").strip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if choice == "1":
        data = scrape_generic(url)
        save_to_json(data, f"scrape_{timestamp}.json")
    elif choice == "2":
        selector = input("CSS selector: ").strip()
        html = fetch_page(url)
        if html:
            texts = extract_text(html, selector)
            save_to_json(texts, f"scrape_text_{timestamp}.json")
    elif choice == "3":
        selector = input("CSS selector for links (default: a[href]): ").strip() or "a[href]"
        html = fetch_page(url)
        if html:
            links = extract_links(html, selector, url)
            save_to_json(links, f"scrape_links_{timestamp}.json")
    elif choice == "4":
        selector = input("Table CSS selector (default: table): ").strip() or "table"
        html = fetch_page(url)
        if html:
            rows = extract_table(html, selector)
            out = f"scrape_table_{timestamp}.csv"
            save_to_csv(rows, out)
    elif choice == "5":
        selector = input("Image CSS selector (default: img): ").strip() or "img"
        html = fetch_page(url)
        if html:
            imgs = extract_images(html, selector)
            save_to_json(imgs, f"scrape_images_{timestamp}.json")
    else:
        print("Invalid choice.")


def main():
    print("=" * 50)
    print("  WEB SCRAPER")
    print("=" * 50)
    interactive_scrape()


if __name__ == "__main__":
    main()
