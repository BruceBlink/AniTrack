import json
import logging  # 导入 logging 模块
import os
import time

import requests
from bs4 import BeautifulSoup

import utils
from common import Result, HEADERS
from config import YOUKU_COMICS_API
from utils import iso_date_ld, random_delay

# 配置日志
logger = logging.getLogger(__name__)


def _fetch_youku_cartoon_today(api_url: str) -> dict[str, list]:
    """从腾讯视频动漫频道获取今日更新的动漫信息。"""
    html_path = "tencent_cartoon.html"  # 临时 HTML 文件名
    try:
        logger.info("开始抓取优酷动漫频道每日更新信息...")
        random_delay()

        session = requests.Session()
        session.headers.update(HEADERS)

        # 获取页面内容
        logger.info("正在获取优酷动漫频道页面...")
        res = session.get(api_url, timeout=15)
        res.raise_for_status()  # 对于不良响应（4xx 或 5xx）抛出 HTTPError

        # 保存 HTML 以便调试
        html_filename = "tencent_cartoon.html"
        html_path = os.path.join(os.getcwd(), html_filename)  # 使用 os.path.join 构造路径
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(res.text)
        logger.info(f"HTML 已保存到 {html_path}")
        # 获取今天的中文星期
        weekday = utils.weekday_today
        result = {weekday: []}

        logger.info("正在查找今日更新模块...")
        # 解析 HTML
        soup = BeautifulSoup(res.text, "html.parser")

        # 找含 INITIAL_DATA 的 script 标签
        script = None
        for tag in soup.find_all("script"):
            text = tag.string
            if text and "__INITIAL_DATA__" in text:
                script = text
                break
        if not script:
            raise ValueError("未找到包含 window.__INITIAL_DATA__ 的 <script>")

        # 清洗并提取 JSON 部分
        prefix = "window.__INITIAL_DATA__="
        json_str = script[len(prefix) + 1:].strip().rstrip(";")
        fixed_json_str = json_str.replace('undefined', 'null')

        data = json.loads(fixed_json_str)
        moduleList = data.get("moduleList", None)
        # 视频地址需要vid +
        # https://v.youku.com/video?vid=XNjQ3MjQzMjE2MA==&scm=20140719.apircmd.298496.video_XNjQ3MjQzMjE2MA==
        # 提取所有漫画卡片
        comics = set()
        for card in moduleList:
            # title
            print(card)
            components = card.get('components', [])
            for itemLists in components:
                # 遍历itemList
                itemList = itemLists.get('itemList', [])
                itemList_title = itemLists.get('title', None)
                if itemList_title == '每日更新':
                    for items in itemList:
                        for item in items:
                            # 过滤出更新的漫画
                            updateTips = item.get('updateTips', None)
                            if updateTips != '有更新':
                                continue
                            title = item.get('title', '').strip()
                            update_info = item.get('lbTexts', '').strip()
                            update_count = str(utils.extract_number(item.get('lbTexts', '')))
                            image_url = item.get('img', '').strip()
                            detail_url = ""
                            comic = Result(
                                platform='youku',
                                title=title,
                                update_count=update_count,
                                update_info=update_info,
                                image_url=image_url,
                                detail_url=detail_url,
                                update_time=iso_date_ld,
                            )
                            # 添加到结果列表
                            comics.add(comic)
        result[weekday] = list(comics) or {}

        return result

    except requests.exceptions.Timeout:
        logger.error("请求超时。将在 10 秒后重试...")
        time.sleep(10)
        return _fetch_youku_cartoon_today(api_url)  # 重试一次
    except requests.exceptions.TooManyRedirects:
        logger.error("重定向过多。请检查 URL。")
        return {}
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求错误: {str(e)}")
        return {}
    except Exception as e:
        logger.exception(f"获取优酷动漫频道更新信息时发生意外错误: {str(e)}")
        return {}
    finally:
        os.remove(html_path)  # 清理临时 HTML 文件
        random_delay()


#     # @retry(
#     retries = 5,
#     delay = 10,
#     retry_condition = lambda result: not any(result.values())
#
#
# # )
# # @print_after_return(print_results, print_condition=lambda r: any(r.values()))
# # @save_after_return(filename="qq_cartoon_today.json", save_condition=lambda r: any(r.values()))
def fetch_youku_cartoon_today() -> dict[str, list] | None:
    logger.info("开始获取优酷动漫频道今日更新...")
    return _fetch_youku_cartoon_today(YOUKU_COMICS_API)


if __name__ == "__main__":
    print(fetch_youku_cartoon_today())
    print("\n所有测试完成！")
