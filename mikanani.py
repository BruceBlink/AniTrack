import logging
import re

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

import config
from config import MIKANANI_BASE_URL, HEADERS

logger = logging.getLogger(__name__)


def fetch_mikanani_today():
    logger.info("Fetching today's Mikanani data...")
    res = requests.get(MIKANANI_BASE_URL, headers=HEADERS, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    logger.info(f"Parsing today's Mikanani data: {soup}")
    today_str = datetime.now().strftime("%Y/%m/%d")
    weekday = config.weekday
    result = {weekday: []}
    for li in soup.find_all("li"):
        if li.find("div", class_="num-node text-center"):
            text = li.get_text(" ", strip=True)[2:15]
            if today_str in text:
                a = li.find("a", href=True)
                title = a.get_text(strip=True) if a else text
                link = urljoin(MIKANANI_BASE_URL, a["href"]) if a else None
                # 提取背景图 URL
                span = li.find("span", class_="js-expand_bangumi")
                image = ""
                if span and span.has_attr("data-src"):
                    image = urljoin(MIKANANI_BASE_URL, span["data-src"])
                anime_info = {
                    "platform": "Mikanani",
                    "title": title,
                    "update_count": "",
                    "update_info": "",
                    "image": image,
                    "link": link,
                    "text": text
                }
                result[weekday].append(anime_info)
    return result
