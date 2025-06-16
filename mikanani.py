import logging

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

from config import MIKANANI_BASE_URL, HEADERS

logger = logging.getLogger(__name__)


def fetch_mikanani_today():
    logger.info("Fetching today's Mikanani data...")
    res = requests.get(MIKANANI_BASE_URL, headers=HEADERS, timeout=10)
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
                link = urljoin(MIKANANI_BASE_URL, a["href"]) if a else None
                anime_info = {
                    "platform": "Mikanani",
                    "title": title,
                    "update_count": "",
                    "update_info": "",
                    "image": "",
                    "link": link,
                    "text": text
                }
                result[weekday].append(anime_info)
    return result
