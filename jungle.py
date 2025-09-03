#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient, ASCENDING

# 환경변수(없으면 기본값 사용)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://appuser:App1234@127.0.0.1:27017/MyDb?authSource=MyDb")
DB_NAME   = os.getenv("DB_NAME", "krafton")
COLL_NAME = os.getenv("COLL_NAME", "curriculum_min")

URL = "https://jungle.krafton.com/program/info#curriculum"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; JungleCurriculumCrawler/1.1; +https://example.com/bot)"
}
WEEK_PAT = re.compile(r"^W0?\d{1,2}(~W\d{1,2})?$")

def fetch_html_with_retries(url: str, headers: dict, retries: int = 3, timeout: int = 15) -> str:
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            last_err = e
            time.sleep(min(2 ** attempt, 8) + random.uniform(0, 0.8))
    raise RuntimeError(f"페이지 요청 실패: {last_err}")

def extract_curriculum_text(soup: BeautifulSoup) -> str:
    sec = soup.select_one("#curriculum")
    if sec:
        return sec.get_text("\n", strip=True)
    h = soup.find(lambda tag: tag.name in ("h1","h2","h3","h4") and "커리큘럼" in tag.get_text())
    if h:
        texts = []
        for sib in h.find_all_next():
            if sib.name in ("h1","h2") and sib is not h and "커리큘럼" not in sib.get_text():
                break
            texts.append(sib.get_text(" ", strip=True))
        return "\n".join([h.get_text(" ", strip=True)] + texts)
    return soup.get_text("\n", strip=True)

def parse_weeks_and_description(text: str):
    """
    텍스트 블록에서 weeks와 description만 추출.
    규칙:
      - weeks: W로 시작하는 주차 또는 범위(W06~W09)
      - description: 해당 weeks부터 다음 weeks 전까지 한국어 문장 누적
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    items, cur = [], None

    def flush():
        nonlocal cur
        if cur and cur.get("weeks"):
            desc = re.sub(r"\s+", " ", cur.get("description", "").strip())
            if desc:
                cur["description"] = desc
                items.append(cur)
        cur = None

    for line in lines:
        if WEEK_PAT.fullmatch(line):
            flush()
            cur = {"weeks": line, "description": ""}
            continue
        if cur:
            if re.search(r"[가-힣]", line) and not re.search(r"(지원|신청|FAQ|문의|바로가기|자세히)", line):
                cur["description"] += (" " if cur["description"] else "") + line
    flush()

    # 동일 weeks 중복 시 마지막 항목만 유지
    dedup = {}
    for it in items:
        dedup[it["weeks"]] = it
    return list(dedup.values())

def crawl_curriculum():
    html = fetch_html_with_retries(URL, HEADERS)
    soup = BeautifulSoup(html, "html.parser")
    text_block = extract_curriculum_text(soup)
    return parse_weeks_and_description(text_block)

def save_to_mongo(items):
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    try:
        coll = client[DB_NAME][COLL_NAME]
        coll.create_index([("weeks", ASCENDING)], unique=True)
        upserts, updates = 0, 0
        for it in items:
            res = coll.update_one(
                {"weeks": it["weeks"]},
                {"$set": {"weeks": it["weeks"], "description": it["description"]}},
                upsert=True
            )
            if res.upserted_id is not None:
                upserts += 1
            elif res.matched_count:
                updates += 1
        print(f"[크롤러] 저장 결과 → 신규:{upserts} 갱신:{updates} 총계:{len(items)}")
    finally:
        client.close()

def run_crawler_once():
    items = crawl_curriculum()
    if not items:
        print("[크롤러] 추출된 항목이 없습니다. 페이지가 동적 렌더링일 수 있습니다.")
        return
    save_to_mongo(items)

if __name__ == "__main__":
    run_crawler_once()
