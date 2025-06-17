import logging
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

import config
from common import Result
from config import MIKANANI_BASE_URL, HEADERS
from decorators import retry, print_after_return
from utils import iso_date_ld, print_results

logger = logging.getLogger(__name__)


def _fetch_mikanani_today() -> dict[str, list]:
    """抓取 Mikanani 今日更新的番剧数据。"""
    logger.info("Fetching today's Mikanani data...")
    result = {config.weekday: []}
    today_str = datetime.now().strftime("%Y/%m/%d")

    try:
        response = requests.get(MIKANANI_BASE_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"请求 Mikanani 页面失败：{e}")
        return result

    soup = BeautifulSoup(response.text, "html.parser")
    logger.debug(f"解析 HTML 内容：{soup}")

    for li in soup.find_all("li"):
        if not li.find("div", class_="num-node text-center"):
            continue  # 过滤掉不包含集数信息的条目

        text = li.get_text(" ", strip=True)[2:15]
        if today_str not in text:
            continue  # 过滤非今日更新

        a_tag = li.find("a", href=True)
        title = a_tag.get_text(strip=True) if a_tag else text
        detail_url = urljoin(MIKANANI_BASE_URL, a_tag["href"]) if a_tag else ""

        # 提取封面图
        image_url = ""
        span = li.find("span", class_="js-expand_bangumi")
        if span and span.has_attr("data-src"):
            image_url = urljoin(MIKANANI_BASE_URL, span["data-src"])

        anime_info = Result(
            platform="Mikanani",
            title=title,
            update_count="",
            update_info=text,
            image_url=image_url,
            detail_url=detail_url,
            update_time=iso_date_ld,
        )

        logger.info(f"识别到更新：{anime_info.title} - {anime_info.update_info}")
        result[config.weekday].append(anime_info)

    return result


@retry(
    retries=5,
    delay=10,
    retry_condition=lambda result: not any(result.values())
)
@print_after_return(print_results, print_condition=lambda r: any(r.values()))
# @save_after_return(filename="qq_cartoon_today.json", save_condition=lambda r: any(r.values()))
def fetch_mikanani_today() -> dict[str, list] | None:
    """获取腾讯视频动漫频道今日更新的动漫信息。"""
    logger.info("开始获取腾讯视频动漫频道今日更新...")
    return _fetch_mikanani_today()


if __name__ == "__main__":
    fetch_mikanani_today()
    print("\n所有测试完成！")
