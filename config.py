import os
import re
import time
import random
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from pymongo import MongoClient, ASCENDING

URL = "https://jungle.krafton.com/program/info#curriculum"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; JungleCurriculumCrawler/1.0; +https://example.com/bot)"
}

# 환경변수로 설정 가능
MONGO_URI = os.getenv("MONGO_URI", "mongodb://appuser:App1234@127.0.0.1:27017/MyDb?authSource=MyDb")
DB_NAME   = os.getenv("DB_NAME", "MyDb")
COLL_NAME = os.getenv("COLL_NAME", "curriculum_min")  # 최소 필드 전용 컬렉션명 예시


def fetch_html_with_retries(url: str, headers: dict, retries: int = 3, timeout: int = 15) -> str:
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            last_err = e
            sleep = min(2 ** attempt, 8) + random.uniform(0, 0.8)
            time.sleep(sleep)
    raise RuntimeError(f"페이지 요청 실패: {last_err}")


def extract_curriculum_text(soup: BeautifulSoup) -> str:
    # 1) 앵커 섹션 우선
    sec = soup.select_one("#curriculum")
    if sec:
        return sec.get_text("\n", strip=True)

    # 2) '커리큘럼' 헤더 이후 텍스트 수집
    h = soup.find(lambda tag: tag.name in ("h1", "h2", "h3", "h4") and "커리큘럼" in tag.get_text())
    if h:
        texts = []
        for sib in h.find_all_next():
            if sib.name in ("h1", "h2") and sib is not h and "커리큘럼" not in sib.get_text():
                break
            texts.append(sib.get_text(" ", strip=True))
        return "\n".join([h.get_text(" ", strip=True)] + texts)

    # 3) 최후: 문서 전체
    return soup.get_text("\n", strip=True)


WEEK_PAT = re.compile(r"^W0?\d{1,2}(~W\d{1,2})?$")

def parse_weeks_and_description(text: str):
    """
    텍스트 블록에서 weeks와 description만 추출.
    규칙:
      - weeks 라인은 'W'로 시작하는 주차 패턴
      - description은 해당 weeks 이후부터 다음 weeks 전까지의 한국어 문장(한 줄씩 누적)
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    items = []
    cur = None

    def flush():
        nonlocal cur
        if cur and cur.get("weeks"):
            # description 정리
            desc = cur.get("description", "").strip()
            desc = re.sub(r"\s+", " ", desc)
            cur["description"] = desc
            items.append(cur)
        cur = None

    for line in lines:
        if WEEK_PAT.fullmatch(line):
            flush()
            cur = {"weeks": line, "description": ""}
            continue

        if cur:
            # 과도한 잡텍스트 방지: 한글 포함 라인만, 링크/버튼성 단어는 약하게 제외
            if re.search(r"[가-힣]", line) and not re.search(r"(지원|신청|FAQ|문의|바로가기|자세히)", line):
                # 문장 이어붙이기
                if cur["description"]:
                    cur["description"] += " "
                cur["description"] += line

    flush()

    # 빈 description 제거
    items = [it for it in items if it.get("description")]
    return items


def dedup_by_weeks(items):
    """
    weeks 기준으로 마지막 항목만 남깁니다.
    """
    by_weeks = {}
    for it in items:
        by_weeks[it["weeks"]] = it
    return list(by_weeks.values())


def crawl_curriculum():
    html = fetch_html_with_retries(URL, HEADERS)
    soup = BeautifulSoup(html, "html.parser")
    text_block = extract_curriculum_text(soup)
    items = parse_weeks_and_description(text_block)

    # 원문 weeks 표기 유지(W010 등). 필요 시 정규화:
    # for it in items:
    #     it["weeks"] = re.sub(r"^W0(\d)$", r"W\1", it["weeks"])

    # 중복 제거
    items = dedup_by_weeks(items)
    return items


def save_to_mongo(items):
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    try:
        coll = client[DB_NAME][COLL_NAME]
        # weeks만 고유 인덱스
        coll.create_index([("weeks", ASCENDING)], unique=True)

        upserts, updates = 0, 0
        for it in items:
            # 메타 필드 없이 최소 필드만 저장
            res = coll.update_one(
                {"weeks": it["weeks"]},
                {"$set": {"weeks": it["weeks"], "description": it["description"]}},
                upsert=True
            )
            if res.upserted_id is not None:
                upserts += 1
            elif res.matched_count:
                updates += 1
        return {"upserts": upserts, "updates": updates, "total": len(items)}
    finally:
        client.close()
