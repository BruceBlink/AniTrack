import logging  # 导入 logging 模块
import time
from datetime import datetime
import requests
import config
from common import Result
from config import HEADERS, IQIYI_CARTOON_API
from decorators import retry, print_after_return
from utils import iso_date_ld, random_delay, clean_text, extract_number, print_results

# 配置日志
logger = logging.getLogger(__name__)


def _fetch_iqiyi_cartoon_today(api_url: str) -> dict[str, list]|None:
    """从腾讯视频动漫频道获取今日更新的动漫信息。"""
    try:
        logger.info(f"开始请求爱奇艺追番表 API {api_url} ...")
        res = requests.get(api_url, headers=HEADERS, timeout=15)
        res.raise_for_status()

        data = res.json()
        if data.get("code") != 0 or "items" not in data:
            logger.error("接口返回异常：%s", data)
            return None
        logger.info(f"成功获取爱奇艺追番表数据{data}。")
        # 获取data的items中的的追番表项
        weekday = config.weekday
        result: dict[str, list] = {weekday: []}
        items = data.get("items", [])
        res = []
        for item in items:
            title = item.get("title", None)
            if title and title == "追番表":
                # 找到今天的追番表
                videos = item.get("video")
                today_data = videos[datetime.now().weekday()]
                today_list = today_data.get("data", [])

                if not today_list:
                    logger.info("今日没有更新")
                    return {"today": []}

                for ep in today_list:
                    # 解析集数数字
                    pub_index = ep.get("dq_updatestatus", "").strip()  # e.g. "第28话"

                    resu = Result(
                        platform="iqiyi",
                        title=clean_text(ep.get("display_name", "")),
                        update_count=str(extract_number(pub_index)),
                        update_info=ep.get("dq_updatestatus", ""),
                        image_url=ep.get("image_cover") or ep.get("image_url_normal"),
                        detail_url=ep.get('page_url', ""),
                        update_time=iso_date_ld
                    )
                    res.append(resu)
                    logger.info("识别到更新：%s %s", resu.title, resu.update_info)

        result[weekday].extend(res)
        return result

    except requests.exceptions.Timeout:
        logger.error("请求超时。将在 10 秒后重试...")
        time.sleep(10)
        return _fetch_iqiyi_cartoon_today()  # 重试一次
    except requests.exceptions.TooManyRedirects:
        logger.error("重定向过多。请检查 URL。")
        return {}
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求错误: {str(e)}")
        return {}
    except Exception as e:
        logger.exception(f"获取爱奇艺动漫频道更新信息时发生意外错误: {str(e)}")
        return {}
    finally:
        random_delay()


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
