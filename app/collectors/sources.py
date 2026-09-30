"""Job sources, returns a list of normalized dicts"""

from datetime import datetime

import hashlib
import requests

GREENHOUSE_URL = "https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
ASHBY_URL = "https://api.ashbyhq.com/posting-api/job-board/{board_token}?includeCompensation=false"
UA = {"User-Agent": "jobsearch"}
TIMEOUT = 25

def create_id(company: str, title: str, url: str) -> str:
    return hashlib.sha1(f"{company}|{title}|{url}".encode()).hexdigest()[:16]

def normalize(company, title, url, location="", posted_at=None, description="", source="", domain=""):
    return {
        "id": create_id(company, title, url),
        "company": company,
        "title": title.strip(),
        "url": url,
        "location": location.strip(),
        "posted_at": posted_at,
        "description": description[:6000],
        "source": source,
        "domain": domain
    }

def create_epoch(val) -> float| None:
    "Normalize to epoch seconds"
    if val in (None, ""):
        return None
    try:
        dt = datetime.fromisoformat(val)
        return dt.timestamp()
    except Exception:
        return None

def _get(url: str) -> Any:
    res = requests.get(url, headers=UA, timeout=TIMEOUT)
    res.raise_for_status()
    return res.json()

#--------------
# All boards
#--------------
def greenhouse(name: str, board_token: str) -> list[dict]:
    data = _get(GREENHOUSE_URL.format(board_token = board_token))
    out= []
    for j in data.get("jobs", []):
        loc = (j.get("location")).get("name")
        out.append(
            normalize(name, j.get("title"), j.get("absolute_url"), loc,
                create_epoch(j.get("updated_at") or j.get("published_at")), j.get("content", ""), "greenhouse"
            ))
    return out

def ashby(name: str, board_token: str) -> list[dict]:
    data = _get(ASHBY_URL.format(board_token = board_token))
    out= []
    for j in data.get("jobs", []):
        out.append(normalize(name, j.get("title"), j.get("jobUrl"), j.get("location", ""),
            create_epoch(j.get("publishedAt")), j.get("descriptionPlain", ""), "ashby"))
    return out

BOARDS = {"greenhouse": greenhouse, "ashby": ashby}

def fetch_company(entry: dict) -> tuple[list[dict], str|None]:
    "Returns job/errors"
    board = entry.get("board", "greenhouse").lower()
    fxn = BOARDS.get(board)
    if not fxn:
        return [], f"Unknown board {board}"
    try:
        jobs = fxn(entry["name"], entry["board_token"])
        for i in jobs:
            i["domain"] = entry.get("domain")
        return jobs, None
    except Exception as e:
        return [], f"{e}"