"""Weekly discovery of news candidates about Korean-flavor QSR menus.

Articles are leads for editorial review, NOT verified menu launch records.
"""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "site" / "data" / "candidates.json"
SEARCHES = [
    ("KFC", '"KFC" ("Korean" OR "gochujang" OR "yangnyeom" OR "kimchi" OR "bulgogi") menu when:10d'),
    ("McDonald's", '"McDonald’s" ("Korean" OR "gochujang" OR "kimchi" OR "bulgogi") menu when:10d'),
    ("McDonald's", '"McDonalds" ("Korean" OR "gochujang" OR "kimchi" OR "bulgogi") when:10d'),
    ("Burger King", '"Burger King" ("Korean" OR "kimchi" OR "bulgogi" OR "gochujang") menu when:10d'),
    ("Pizza Hut", '"Pizza Hut" ("Korean" OR "kimchi" OR "bulgogi" OR "gochujang") when:10d'),
    ("Domino's", '"Dominos" ("Korean" OR "kimchi" OR "bulgogi" OR "gochujang") menu when:10d'),
    ("Popeyes", '"Popeyes" ("Korean" OR "gochujang" OR "kimchi") menu when:10d'),
    ("Subway", '"Subway" ("Korean" OR "kimchi" OR "bulgogi" OR "gochujang") menu when:10d'),
    ("Shake Shack", '"Shake Shack" ("Korean" OR "gochujang" OR "kimchi") when:10d'),
    ("Jollibee", '"Jollibee" ("Korean" OR "gochujang" OR "kimchi") when:10d'),
    ("Lotteria", '"Lotteria" ("Korean" OR "kimchi" OR "gochujang") when:10d'),
    ("Korean QSR Asia", '("韓式" OR "韓国風" OR "한국식") ("KFC" OR "McDonald" OR "Burger King") when:10d'),
]
BRANDS = [
    'kfc', 'kentucky fried chicken', 'mcdonald', '맥도날드', 'マクドナルド', '麥當勞',
    'burger king', '버거킹', 'pizza hut', '피자헛', 'domino', '도미노',
    'popeyes', '파파이스', 'subway', '서브웨이', 'shake shack', '쉐이크쉑',
    'jollibee', 'lotteria', '롯데리아', '肯德基', '必勝客'
]
KOREAN = [
    'korean', 'k-food', 'k food', 'kbbq', 'k-bbq', 'k bbq',
    'gochujang', 'kimchi', 'bulgogi', 'yangnyeom', 'soy garlic',
    '한국', '韓式', '韓国', '고추장', '김치', '불고기', '양념치킨', '韓風', '韓式炸雞'
]

def relevant(title):
    value = " ".join(title.casefold().split())
    return any(x in value for x in BRANDS) and any(x in value for x in KOREAN)

def clean_url(url):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return None
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))

def fetch_feed(query):
    opts = urllib.parse.urlencode({
        "q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"
    })
    request = urllib.request.Request(
        "https://news.google.com/rss/search?" + opts,
        headers={"User-Agent": "KFoodRadar/1.0 (weekly research news monitor)"}
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = response.read(2_000_000)
    return ET.fromstring(payload).findall("./channel/item")

def iso_date(raw):
    try:
        value = parsedate_to_datetime(raw)
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat(timespec="seconds")
    except (TypeError, ValueError, OverflowError):
        return ""

def main():
    now_kst = datetime.now(timezone.utc).astimezone(ZoneInfo("Asia/Seoul"))
    scanned_at = now_kst.isoformat(timespec="seconds")
    try:
        prior = json.loads(TARGET.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        prior = {"records": []}
    known = {item["url"]: item for item in prior.get("records", []) if item.get("url")}
    errors = []
    success = 0
    added = 0
    for index, (brand, query) in enumerate(SEARCHES):
        try:
            items = fetch_feed(query)
            success += 1
            for item in items:
                title = " ".join((item.findtext("title") or "").strip().split())
                url = clean_url((item.findtext("link") or "").strip())
                if not url or not relevant(title) or url in known:
                    continue
                source = item.find("source")
                known[url] = {
                    "id": "rss-" + sha256(url.encode()).hexdigest()[:14],
                    "brand": brand,
                    "title": title[:280],
                    "url": url,
                    "source": (source.text or "")[:90] if source is not None else "Google News RSS",
                    "publishedAt": iso_date(item.findtext("pubDate")),
                    "discoveredAt": scanned_at,
                    "query": brand,
                    "status": "검토 대기"
                }
                added += 1
        except Exception as error:
            errors.append({"brand": brand, "error": str(error)[:180]})
            print(f"WARN: {brand} RSS scan failed: {error}", file=sys.stderr)
        if index < len(SEARCHES) - 1:
            time.sleep(0.7)
    if success == 0:
        print("ERROR: Every RSS query failed. Existing news data unchanged.", file=sys.stderr)
        return 1
    rows = sorted(
        known.values(),
        key=lambda row: (row.get("publishedAt") or "", row.get("discoveredAt") or ""),
        reverse=True
    )[:400]
    output = {
        "source": "Google News RSS discovery / editorial review required",
        "lastScanKst": scanned_at,
        "status": "partial" if errors else "ok",
        "newItems": added,
        "queriesSucceeded": success,
        "queriesFailed": len(errors),
        "records": rows
    }
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Checked {success}/{len(SEARCHES)} RSS searches; added {added} articles, retained {len(rows)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
