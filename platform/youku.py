import logging  # 导入 logging 模块
import os
import time

import requests
from bs4 import BeautifulSoup

from common import Result
import config
from config import HEADERS, YOUKU_COMICS_API
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
        weekday = config.weekday
        result = {weekday: []}

        logger.info("正在查找今日更新模块...")
        # 解析 HTML
        soup = BeautifulSoup(res.text, "html.parser")

        # 查找包含所有漫画的主容器
        container = soup.find('div', class_='hscroll_content_fdYOj')

        # 提取所有漫画卡片
        comics = []
        for card in container.find_all('div', class_='g-col'):
            # 提取平台类型
            tag_div = card.find('div', class_='pack_mark_1hLkl')
            platform = tag_div.find('span').text.strip() if tag_div else ""

            # 提取标题
            a_tag = card.find('a')
            title = a_tag.get('aria-label', '').split()[-1] if a_tag else ""

            # 提取更新集数
            update_span = card.find('span', class_='lb_texts_23IEZ')
            update_count = update_span.text.strip() if update_span else ""

            # 提取更新信息
            subtitle_div = card.find('div', class_='subtitle_1CJyy')
            update_info = subtitle_div.text.strip() if subtitle_div else ""

            # 提取图片URL
            img_tag = card.find('img', class_='pack_img_YJm41')
            image_url = img_tag.get('src', '') if img_tag else ""

            # 提取详情页URL
            detail_url = "https:" + a_tag.get('href', '') if a_tag else ""
            comic = Result(
                platform=platform,
                title=title,
                update_count=update_count,
                update_info=update_info,
                image_url=image_url,
                detail_url=detail_url,
                update_time=iso_date_ld,
            )

            # 添加到结果列表
            comics.append(comic)
        result[weekday] = comics or {}

        return result

    except requests.exceptions.Timeout:
        logger.error("请求超时。将在 10 秒后重试...")
        time.sleep(10)
        return _fetch_youku_cartoon_today()  # 重试一次
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
    """获取腾讯视频动漫频道今日更新的动漫信息。"""
    logger.info("开始获取优酷动漫频道今日更新...")
    return _fetch_youku_cartoon_today(YOUKU_COMICS_API)


if __name__ == "__main__":
    print(fetch_youku_cartoon_today())
    print("\n所有测试完成！")
