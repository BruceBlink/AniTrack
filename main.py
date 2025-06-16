import json
import logging

from logger_setup import init_logger
from mikanani import fetch_mikanani_today
from utils import update_today_section_in_readme


def main():
    # 统一初始化 logger
    init_logger(level=logging.DEBUG)
    logging.info("开始获取今日的 追番数据...")
    data = fetch_mikanani_today()
    update_today_section_in_readme(data)
    logging.info("今日的 Mikanani 数据已更新到 README 中。")
    # with open("mikanani_today.json", "w", encoding="utf-8") as f:
    #     json.dump(data, f, ensure_ascii=False, indent=2)
    # print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()