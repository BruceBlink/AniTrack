import logging
import utils
from bilibili import fetch_bilibili_guochuang_today, fetch_bilibili_anime_today
from iqiyi import fetch_iqiyi_cartoon_today
from logger_setup import init_logger
from mikanani import fetch_mikanani_today
from tencent import fetch_qq_cartoon_today
from utils import update_today_section_in_readme


def main():
    # 统一初始化 logger
    init_logger(level=logging.DEBUG)
    logging.info("开始获取今日的 追番数据...")
    # 获取今日的追番数据
    mikanani_data = fetch_mikanani_today()
    # 获取腾讯动漫今日更新数据
    tencent_data = fetch_qq_cartoon_today()
    # 获取 bilibili 国创和番剧今日更新数据
    bilibili_guochuang_data = fetch_bilibili_guochuang_today()
    bilibili_anime_data = fetch_bilibili_anime_today()
    # 获取iqiyi 今日更新数据
    iqiyi_cartoon_data = fetch_iqiyi_cartoon_today()
    data = utils.merge_dict_data(mikanani_data, tencent_data, bilibili_guochuang_data, bilibili_anime_data, iqiyi_cartoon_data)  # 合并多个数据字典
    # 更新 README 中的今日番剧更新部分
    update_today_section_in_readme(data)
    logging.info("今日的番剧更新数据已更新到 README 中。")
    # with open("mikanani_today.json", "w", encoding="utf-8") as f:
    #     json.dump(data, f, ensure_ascii=False, indent=2)
    # print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
