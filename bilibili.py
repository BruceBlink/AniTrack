import json
import logging  # 导入 logging 模块
import os
import random
import re
import time
import requests
import config
from config import HEADERS, BILIBILI_GUOCHUANG_API, BILIBILI_ANIME_API
from utils import print_results, clean_text
from common import Result, AbstractFetcher
from utils import iso_date_ld
from decorators import retry, print_after_return, save_after_return
# 配置日志
logger = logging.getLogger(__name__)

class BilibiliFetcher(AbstractFetcher):
    """哔哩哔哩数据抓取器，继承自抽象基类 AbstractFetcher。"""

    def __init__(self, api_url: str, platform: str = "bilibili"):
        super().__init__()
        self.api_url = api_url
        self.platform = platform

    def fetch_data(self) -> dict[str, list] | None:
        """实现数据抓取逻辑，获取哔哩哔哩国创频道今日更新的动漫信息。"""
        super().fetch_data()
        return _fetch_bilibili_update_today(self.api_url)

def _fetch_bilibili_update_today(api_url: str) -> dict[str, list] | None:
    """从哔哩哔哩国创频道官方 JSON 接口获取今日更新的动漫信息。"""
    try:
        logger.info(f"开始请求哔哩哔哩更新时间线 API {api_url} ...")
        res = requests.get(api_url, headers=HEADERS, timeout=15)
        res.raise_for_status()

        data = res.json()
        if data.get("code") != 0 or "result" not in data:
            logger.error("接口返回异常：%s", data)
            return None
        logger.info(f"成功获取哔哩哔哩更新时间线数据{data}。")
        # 找到 is_today == 1 的那一天
        today_list = [d for d in data["result"] if d.get("is_today") == 1]
        if not today_list:
            logger.info("今日没有更新")
            return {"today": []}

        today = today_list[0]
        update_time = today["date"]  # e.g. "6-17"
        weekday = config.weekday
        result: dict[str, list] = {weekday: []}

        for ep in today.get("episodes", []):
            # 只取已经 published 的
            if ep.get("published") != 1:
                continue

            # 解析集数数字
            pub_index = ep.get("pub_index", "").strip()  # e.g. "第28话"
            try:
                count = int(pub_index.lstrip("第").rstrip("话"))
            except:
                count = None
            item = Result(
                platform = "bilibili",
                title = clean_text(ep.get("title", "")),
                update_count = count,
                update_info = "更新至" + pub_index,
                image_url = ep.get("square_cover") or ep.get("cover"),
                detail_url = f"https://www.bilibili.com/bangumi/play/ep{ep.get('episode_id')}",
                update_time = iso_date_ld
            )
            logger.info("识别到更新：%s %s", item.title, item.update_info)
            result[weekday].append(item)

        return result

    except requests.exceptions.Timeout:
        logger.warning("请求超时，10 秒后重试...")
        time.sleep(10)
        return _fetch_bilibili_update_today()
    except requests.exceptions.RequestException as e:
        logger.error("请求错误：%s", e)
        return None
    except Exception as e:
        logger.exception("未知错误：%s", e)
        return None


@retry(
    retries=5,
    delay=10,
    retry_condition=lambda result: not result or not any(result.values())
)
@print_after_return(print_results, print_condition=lambda r: any(r.values()))
#@save_after_return(filename="bilibili_guochuang_today.json", save_condition=lambda r: any(r.values()))
def fetch_bilibili_guochuang_today() -> dict[str, list] | None:
    """获取哔哩哔哩国创频道今日更新的动漫信息。"""
    logger.info("开始测试哔哩哔哩国创频道今日更新...")
    return _fetch_bilibili_update_today(BILIBILI_GUOCHUANG_API)


@retry(
    retries=5,
    delay=10,
    retry_condition=lambda result: not result or not any(result.values())
)
@print_after_return(print_results, print_condition=lambda r: any(r.values()))
def fetch_bilibili_anime_today() -> dict[str, list] | None:
    logger.info("调用 _fetch_bilibili_update_today 获取今日番剧更新信息...")
    return _fetch_bilibili_update_today(BILIBILI_ANIME_API)



if __name__ == "__main__":
    bilibili_guochuang = BilibiliFetcher(BILIBILI_GUOCHUANG_API)
    bilibili_guochuang_data = bilibili.fetch_data()
    bilibili_anime = BilibiliFetcher(BILIBILI_ANIME_API)
    bilibili_anime_data = bilibili_anime.fetch_data()
    print("\n所有测试完成！")
