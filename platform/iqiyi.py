import logging  # 导入 logging 模块
import time
from datetime import datetime

import requests

import utils
from common import Result, HEADERS
from common.decorators import retry, print_after_return
from config import IQIYI_CARTOON_API
from utils import iso_date_ld, random_delay, clean_text, extract_number, print_results

# 配置日志
logger = logging.getLogger(__name__)


def _fetch_iqiyi_cartoon_today(api_url: str) -> dict[str, list] | None:
    """从爱奇艺动漫频道获取今日更新的动漫信息。"""
    try:
        logger.info(f"开始请求爱奇艺追番表 API: {api_url}")
        response = requests.get(api_url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        data = response.json()
        if data.get("code") != 0 or not data.get("items"):
            logger.error("接口返回异常: %s", data)
            return None

        logger.info("成功获取爱奇艺追番表数据")
        current_weekday = datetime.now().weekday()
        # 查找追番表数据
        for item in data["items"]:
            if item.get("title") == "追番表":
                today_data = item.get("video", [])[current_weekday]
                today_list = today_data.get("data", [])

                if not today_list:
                    logger.info("今日没有更新")
                    return {utils.weekday_today: []}

                # 使用列表生成式处理更新数据
                results = [
                    Result(
                        platform="iqiyi",
                        title=clean_text(ep.get("display_name", "")),
                        update_count=str(extract_number(ep.get("dq_updatestatus", "").strip())),
                        update_info=ep.get("dq_updatestatus", ""),
                        image_url=ep.get("image_cover") or ep.get("image_url_normal"),
                        detail_url=ep.get('page_url', ""),
                        update_time=iso_date_ld
                    )
                    for ep in today_list
                ]

                # 记录更新信息
                for res in results:
                    logger.info("识别到更新：%s %s", res.title, res.update_info)

                return {utils.weekday_today: results}

        logger.warning("未找到追番表数据")
        return {utils.weekday_today: []}

    except requests.exceptions.Timeout:
        logger.warning("请求超时，将在 10 秒后重试...")
        time.sleep(10)
        return _fetch_iqiyi_cartoon_today(api_url)  # 传递api_url参数

    except requests.exceptions.TooManyRedirects:
        logger.error("重定向过多，请检查 URL")

    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求错误: {e}")

    except Exception as e:
        logger.exception(f"处理数据时发生意外错误: {e}")

    finally:
        random_delay()

    return None


@retry(
    retries = 5,
    delay = 10,
    retry_condition = lambda result: not any(result.values())
)
@print_after_return(print_results, print_condition=lambda r: any(r.values()))
# @save_after_return(filename="qq_cartoon_today.json", save_condition=lambda r: any(r.values()))
def fetch_iqiyi_cartoon_today() -> dict[str, list] | None:
    """获取腾讯视频动漫频道今日更新的动漫信息。"""
    logger.info("开始获取爱奇艺动漫频道今日更新...")
    return _fetch_iqiyi_cartoon_today(IQIYI_CARTOON_API)


if __name__ == "__main__":
    print(fetch_iqiyi_cartoon_today())
    print("\n所有测试完成！")
