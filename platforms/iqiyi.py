import asyncio
import json
import logging  # 导入 logging 模块
import time
from datetime import datetime
import aiohttp
import requests
from bs4 import Tag
import utils
from common import Result, AbstractFetcher, Logger
from common.decorators import print_after_return_async, retry_async, timer, \
    print_performance_metrics
from config import IQIYI_CARTOON_API
from utils import iso_date_ld, clean_text, extract_number, print_results


class IQiyiFetcher(AbstractFetcher):
    def __init__(self, api_url: str, platform: str = "iqiyi"):
        super().__init__()
        self.api_url = api_url
        self.platform = platform

    def _build_result_from_episode(self, ep: dict | Tag) -> Result:
        super()._build_result_from_episode(ep)
        return Result(
            platform=self.platform,
            title=clean_text(ep.get("display_name", "")),
            update_count=str(extract_number(ep.get("dq_updatestatus", "").strip())),
            update_info=ep.get("dq_updatestatus", ""),
            image_url=ep.get("image_cover") or ep.get("image_url_normal"),
            detail_url=ep.get('page_url', ""),
            update_time=iso_date_ld
        )

    async def _fetch_iqiyi_cartoon_today(self, session: aiohttp.ClientSession) -> dict[str, list] | None:
        """从爱奇艺动漫频道获取今日更新的动漫信息。"""
        try:
            await super().fetch_update_data(session)
            data = json.loads(self.response_text)
            logging.debug(f"解析从API获取到的 JSON 数据为：{data}")
            if data.get("code") != 0 or not data.get("items"):
                logging.error("接口返回异常: %s", data)
                return None

            logging.info("成功获取爱奇艺追番表数据")
            current_weekday = datetime.now().weekday()
            # 查找追番表数据
            for item in data["items"]:
                if item.get("title") == "追番表":
                    today_data = item.get("video", [])[current_weekday]
                    today_list = today_data.get("data", [])

                    if not today_list:
                        logging.info("今日没有更新")
                        return {utils.weekday_today: []}

                    # 使用列表生成式处理更新数据
                    results = [
                        self._build_result_from_episode(ep)
                        for ep in today_list
                    ]
                    self.result[utils.weekday_today] = results
                    # 记录更新信息
                    for res in results:
                        logging.info(f"识别到更新：{res.title} {res.update_info}")

                    return self.result

            logging.warning("未找到追番表数据")
            return {utils.weekday_today: []}

        except requests.exceptions.Timeout:
            logging.warning("请求超时，将在 10 秒后重试...")
        except requests.exceptions.TooManyRedirects:
            logging.error("重定向过多，请检查 URL")
        except requests.exceptions.RequestException as e:
            logging.error(f"网络请求错误: {e}")
        except Exception as e:
            logging.exception(f"处理数据时发生意外错误: {e}")

        return None

    @retry_async(
        retries=5,
        delay=10,
        retry_condition=lambda result: not result
    )
    @print_after_return_async(print_results, print_condition=lambda r: not r and any(r.values()))
    @timer(unit="ms")
    async def fetch_iqiyi_cartoon_today(self) -> dict[str, list] | None:
        """获取腾讯视频动漫频道今日更新的动漫信息。"""
        logging.info("开始获取爱奇艺动漫频道今日更新...")
        async with aiohttp.ClientSession() as session:
            return await self._fetch_iqiyi_cartoon_today(session)


@timer(enable_stats=True, print_report=False)
async def test_all2():
    iqiyi_cartoon = IQiyiFetcher(IQIYI_CARTOON_API)
    t1 = asyncio.create_task(iqiyi_cartoon.fetch_iqiyi_cartoon_today())
    # 等待所有任务完成
    await asyncio.gather(t1)


if __name__ == "__main__":
    Logger.init(
        level=logging.DEBUG,
        max_bytes=10_000_000,
        backup_count=5,
        console=True,
        colored=True
    )

    # 多次调用
    #for i in range(1, 11):
    asyncio.run(test_all2())
    # test_all1()

    # 获取统计信息
    # stats = test_all1.get_stats()
    print_performance_metrics(test_all2)
