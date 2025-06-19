import logging

import utils
from common.logger_setup import init_logger
from config import BILIBILI_GUOCHUANG_API, BILIBILI_ANIME_API
from platforms.bilibili import BilibiliFetcher
from platforms.iqiyi import fetch_iqiyi_cartoon_today
from platforms.mikanani import fetch_mikanani_today
from platforms.tencent import fetch_qq_cartoon_today
from platforms.youku import fetch_youku_cartoon_today


def main():
    init()
    logging.info("开始获取今日的 追番数据...")
    # 获取所有平台的今日更新数据
    data = get_all_update_data()
    logging.info("今日的追番数据获取完成。")
    # 合并所有平台的数据
    merged_data = utils.merge_dict_data(*data.values())
    # 保存合并后的数据到 JSON 文件
    logging.info("保存今日追番数据到 JSON 文件...")
    utils.save_data_to_json("today_cartoon.json", merged_data)
    # 更新 README 中的今日番剧更新部分
    logging.info("更新 README 中的今日番剧更新部分...")
    utils.update_today_section_in_readme(merged_data)
    today_key = utils.weekday_today
    count = len(merged_data.get(today_key, []))
    logging.info(f"今日的番剧更新数据已更新到 README 中，总共更新了 {count} 部番剧。")


def get_all_update_data():
    """
    获取所有平台的今日更新数据。
    返回一个包含各平台更新数据的字典。
    """
    fetcher = FetcherImpl()
    return {
        "mikanani": fetch_mikanani_today(),
        "tencent": fetch_qq_cartoon_today(),
        "bilibili_guochuang": fetcher.bilibili_guochuang.fetch_bilibili_cartoon_today(),
        "bilibili_anime": fetcher.bilibili_anime.fetch_bilibili_cartoon_today(),
        "iqiyi": fetch_iqiyi_cartoon_today(),
        "youku": fetch_youku_cartoon_today()
    }


def init():
    """初始化日志记录器"""
    # 统一初始化 logger
    init_logger(level=logging.DEBUG)
    logging.info("日志记录器已初始化。")


class FetcherImpl:
    def __init__(self):
        self.bilibili_guochuang = BilibiliFetcher(BILIBILI_GUOCHUANG_API)
        self.bilibili_anime = BilibiliFetcher(BILIBILI_ANIME_API)


if __name__ == "__main__":
    main()
