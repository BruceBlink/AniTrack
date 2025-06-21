import asyncio
import logging

import utils
from common import Logger
from common.decorators import timer
from config import BILIBILI_GUOCHUANG_API, BILIBILI_ANIME_API, MIKANANI_BASE_URL, TENCENT_CARTOON_BASE_URL, \
    IQIYI_CARTOON_API, YOUKU_COMICS_API
from platforms.bilibili import BilibiliFetcher
from platforms.iqiyi import IQiyiFetcher
from platforms.mikanani import MikananiFetcher
from platforms.tencent import TencentFetcher
from platforms.youku import YoukuFetcher


@timer(unit="ms")
def main():
    init()
    logging.info("开始获取今日的 追番数据...")
    # 获取所有平台的今日更新数据
    data = get_all_update_data()
    logging.info("今日的追番数据获取完成。")
    # 合并所有平台的数据
    merged_data = utils.merge_dict_data(*data)
    # 保存合并后的数据到 JSON 文件
    logging.info("保存今日追番数据到 JSON 文件...")
    utils.save_data_to_json(f"data/{utils.iso_date}_cartoon.json", merged_data)
    # 更新 README 中的今日番剧更新部分
    logging.info("更新 README 中的今日番剧更新部分...")
    utils.update_today_section_in_readme(merged_data)
    today_key = utils.weekday_today
    count = len(merged_data.get(today_key, []))
    logging.info(f"今日的番剧更新数据已更新到 README 中，总共更新了 {count} 部番剧。")


@timer(unit="ms")
def get_all_update_data():
    """
    获取所有平台的今日更新数据。
    返回一个包含各平台更新数据的字典。
    """
    # fetcher = FetcherImpl()
    # return {
    #     "mikanani": fetcher.mikanani.fetch_mikanani_update_today(),
    #     "tencent": fetch_qq_cartoon_today(),
    #     "bilibili_guochuang": fetcher.bilibili_guochuang.fetch_bilibili_cartoon_today(),
    #     "bilibili_anime": fetcher.bilibili_anime.fetch_bilibili_cartoon_today(),
    #     "iqiyi": fetch_iqiyi_cartoon_today(),
    #     "youku": fetch_youku_cartoon_today()
    # }
    result = asyncio.run(get_all_async_fetcher_tasks())
    return result


async def get_all_async_fetcher_tasks():
    """异步获取所有更新数据"""
    fetcher = FetcherImpl()
    mikanani = fetcher.mikanani.fetch_mikanani_update_today()
    bilibili_guochuang = fetcher.bilibili_guochuang.fetch_bilibili_cartoon_today()
    bilibili_anime = fetcher.bilibili_anime.fetch_bilibili_cartoon_today()
    tencent_cartoon = fetcher.tencent.fetch_qq_cartoon_today()
    iqiyi_cartoon = fetcher.iqiyi.fetch_iqiyi_cartoon_today()
    youku = fetcher.youku.fetch_youku_cartoon_today()
    tasks = [mikanani, bilibili_guochuang, bilibili_anime, tencent_cartoon, iqiyi_cartoon, youku]
    return await asyncio.gather(*tasks)


def init():
    """初始化日志记录器"""
    # 统一初始化 logger
    Logger.init(
        level=logging.DEBUG,
        log_file=f"logs/{utils.iso_date_dd}_cartoon_fetcher.log",
        max_bytes=10_000_000,
        backup_count=5,
        console=True,
        colored=True
    )
    logging.info("日志记录器已初始化。")


class FetcherImpl:
    def __init__(self):
        self.bilibili_guochuang = BilibiliFetcher(BILIBILI_GUOCHUANG_API)
        self.bilibili_anime = BilibiliFetcher(BILIBILI_ANIME_API)
        self.mikanani = MikananiFetcher(MIKANANI_BASE_URL)
        self.tencent = TencentFetcher(TENCENT_CARTOON_BASE_URL)
        self.iqiyi = IQiyiFetcher(IQIYI_CARTOON_API)
        self.youku = YoukuFetcher(YOUKU_COMICS_API)


if __name__ == "__main__":
    main()
