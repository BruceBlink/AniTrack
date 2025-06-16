import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
BASE_URL = "https://mikanani.me"


def fetch_mikanani_today():
    res = requests.get(BASE_URL, headers=HEADERS, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    today_str = datetime.now().strftime("%Y/%m/%d")
    weekday = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][datetime.now().weekday()]
    result = {weekday: []}
    for li in soup.find_all("li"):
        if li.find("div", class_="num-node text-center"):
            text = li.get_text(" ", strip=True)[2:]
            if today_str in text:
                a = li.find("a", href=True)
                title = a.get_text(strip=True) if a else text
                link = urljoin(BASE_URL, a["href"]) if a else None
                result[weekday].append({
                    "platform": "Mikanani",
                    "title": title,
                    "link": link,
                    "text": text
                })
    return result
