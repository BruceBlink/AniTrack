import logging
import utils
from platform.bilibili import BilibiliFetcher
from config import BILIBILI_GUOCHUANG_API, BILIBILI_ANIME_API
from platform.iqiyi import fetch_iqiyi_cartoon_today
from common.logger_setup import init_logger
from platform.mikanani import fetch_mikanani_today
from platform.tencent import fetch_qq_cartoon_today
from utils import update_today_section_in_readme


def main():
    init()
    logging.info("开始获取今日的 追番数据...")
    # 获取今日的追番数据
    mikanani_data = fetch_mikanani_today()
    # 获取腾讯动漫今日更新数据
    tencent_data = fetch_qq_cartoon_today()
    # 获取 bilibili 国创和番剧今日更新数据
    fetcher = FetcherImpl()
    bilibili_guochuang_data = fetcher.bilibili_guochuang.fetch_bilibili_cartoon_today()
    bilibili_anime_data = fetcher.bilibili_guochuang.fetch_bilibili_cartoon_today()
    # 获取iqiyi 今日更新数据
    iqiyi_cartoon_data = fetch_iqiyi_cartoon_today()
    data = utils.merge_dict_data(mikanani_data, tencent_data, bilibili_guochuang_data, bilibili_anime_data,
                                 iqiyi_cartoon_data)  # 合并多个数据字典
    # 更新 README 中的今日番剧更新部分
    update_today_section_in_readme(data)
    logging.info("今日的番剧更新数据已更新到 README 中。")
    # with open("mikanani_today.json", "w", encoding="utf-8") as f:
    #     json.dump(data, f, ensure_ascii=False, indent=2)
    # print(json.dumps(data, ensure_ascii=False, indent=2))


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
