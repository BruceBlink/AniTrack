import json
import logging  # 导入 logging 模块
import os
import random
import re
import time
import requests
import config
from config import HEADERS, BILIBILI_GUOCHUANG_API, BILIBILI_ANIME_API
from utils import print_results
from common import Result
from utils import iso_date_ld
# 配置日志
logger = logging.getLogger(__name__)


def random_delay(min_sec=1.2, max_sec=4.5):
    """引入随机延迟，模拟人类行为并避免被封锁。"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    logger.debug(f"延迟了 {delay:.2f} 秒。")


def clean_text(text):
    """清理文本，替换 HTML 实体并规范化空白字符。"""
    if not text:
        return ""

    # 替换常见的 HTML 实体
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&#x27;', "'", text)  # 撇号

    # 将所有空白字符（空格、制表符、换行符）规范化为单个空格，然后去除首尾空格。
    text = re.sub(r'\s+', ' ', text).strip()
    return text


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


def save_results(results, filename="tencent_cartoon.json"):
    """将结果保存到 JSON 文件。"""
    if not results:
        logger.info("没有可保存的结果。")
        return

    file_path = os.path.join(os.getcwd(), filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logger.info(f"结果已保存到 {file_path}")


def fetch_bilibili_guochuang_today() -> dict[str, list] | None:
    """获取哔哩哔哩国创频道今日更新的动漫信息。"""
    logger.info("开始测试哔哩哔哩国创频道今日更新...")
    # 执行 5 次测试
    num_tests = 5
    for i in range(1, num_tests + 1):
        logger.info(f"\n{'=' * 40}")
        logger.info(f"测试 #{i}")
        logger.info(f"{'=' * 40}")

        today_updates = _fetch_bilibili_update_today(BILIBILI_GUOCHUANG_API)

        if today_updates:
            print_results(today_updates)
            return today_updates
            # save_results(today_updates, f"tencent_cartoon_test_{i}.json")
        else:
            logger.warning("未能获取今日国创更新信息。")

        # 在测试之间添加较长延迟，除非是最后一次测试
        if i < num_tests:
            logger.info(f"\n等待 10 秒后进行下一次测试 (测试 #{i + 1})...")
            time.sleep(10)


def fetch_bilibili_anime_today() -> dict[str, list] | None:
    """获取哔哩哔哩番剧频道今日更新的动漫信息。"""
    # 执行 5 次测试
    logger.info("开始测试哔哩哔哩番剧频道今日更新...")
    num_tests = 5
    for i in range(1, num_tests + 1):
        logger.info(f"\n{'=' * 40}")
        logger.info(f"测试 #{i}")
        logger.info(f"{'=' * 40}")

        today_updates = _fetch_bilibili_update_today(BILIBILI_ANIME_API)

        if today_updates:
            print_results(today_updates)
            return today_updates
            # save_results(today_updates, f"tencent_cartoon_test_{i}.json")
        else:
            logger.warning("未能获取今日番剧更新信息。")

        # 在测试之间添加较长延迟，除非是最后一次测试
        if i < num_tests:
            logger.info(f"\n等待 10 秒后进行下一次测试 (测试 #{i + 1})...")
            time.sleep(10)


if __name__ == "__main__":
    fetch_bilibili_guochuang_today()
    fetch_bilibili_anime_today()
    print("\n所有测试完成！")
