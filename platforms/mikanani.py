import asyncio
import logging
import time
from urllib.parse import urljoin
import aiohttp
import requests
from bs4 import BeautifulSoup, Tag
import utils
from common import Result, AbstractFetcher, Logger
from common.decorators import retry_async, print_after_return_async, timer
from config import MIKANANI_BASE_URL
from utils import iso_date_ld, print_results


class MikananiFetcher(AbstractFetcher):
    """蜜柑计划数据抓取器，继承自抽象基类 AbstractFetcher。"""

    def __init__(self, api_url: str = MIKANANI_BASE_URL, platform: str = "Mikanani"):
        super().__init__()
        self.api_url = api_url
        self.platform = platform

    def _build_result_from_episode(self, li: Tag) -> Result:
        super()._build_result_from_episode(li)
        """从单个 <li> 元素构建 Result 对象。"""
        text = li.get_text()[2:15]
        a_tag = li.find("a", href=True)
        title = a_tag.get_text(strip=True) if a_tag else text
        detail_url = urljoin(self.api_url, a_tag["href"]) if a_tag else ""

        # 提取封面图
        image_url = ""
        span = li.find("span", class_="js-expand_bangumi")
        if span and span.has_attr("data-src"):
            image_url = urljoin(self.api_url, span["data-src"])

        return Result(
            platform=self.platform,
            title=title,
            update_count="",
            update_info=text,
            image_url=image_url,
            detail_url=detail_url,
            update_time=iso_date_ld,
        )

    async def _fetch_mikanani_update_today(self, session: aiohttp.ClientSession) -> dict[str, list] | None:
        """抓取 Mikanani 今日更新的番剧数据。"""
        logging.info("Fetching today's Mikanani data...")

        try:
            await super().fetch_update_data(session)
            soup = BeautifulSoup(self.response_text, 'html.parser')
            logging.debug(f"解析 HTML 内容：{soup}")

            items = (li for li in soup.find_all("li") if li.find("div", class_="num-node text-center"))

            for li in items:
                anime_info = self._build_result_from_episode(li)
                logging.info(f"识别到更新：{anime_info.title} - {anime_info.update_info}")
                self.result[utils.weekday_today].append(anime_info)

            return self.result
        except requests.exceptions.Timeout:
            logging.warning("请求超时，10 秒后重试...")
            time.sleep(10)
        except requests.RequestException as e:
            logging.error(f"请求处理异常：{e}")
            return None
        except Exception as e:
            logging.exception(f"其他错误：{e}")
            return None

    @retry_async(
        retries=5,
        delay=10,
        retry_condition=lambda result: not result
    )
    @print_after_return_async(print_results, print_condition=lambda r: any(r.values()))
    @timer(unit="ms")
    async def fetch_mikanani_update_today(self) -> dict[str, list] | None:
        """获取蜜柑计划今日更新的动漫信息。"""
        logging.info("开始获取蜜柑计划今日更新...")
        async with aiohttp.ClientSession() as session:
            return await self._fetch_mikanani_update_today(session)


@timer(enable_stats=True, print_report=False)
async def test_all():
    mikanani_fetcher = MikananiFetcher(api_url=MIKANANI_BASE_URL)
    t1 = asyncio.create_task(mikanani_fetcher.fetch_mikanani_update_today())
    await asyncio.gather(t1)


if __name__ == "__main__":
    Logger.init(
        level=logging.DEBUG,
        max_bytes=10_000_000,
        backup_count=5,
        console=True,
        colored=True
    )

    for i in range(1, 11):
        asyncio.run(test_all())

    # 获取统计信息
    # stats = test_all1.get_stats()
    stats = test_all.get_stats()
    print(f"\n📊 {stats['function']} 性能统计:")
    print(f"  调用次数: {stats['total_calls']}")
    print(f"  总耗时: {stats['total_time'] * 1000:.2f}ms")
    print(f"  平均耗时: {stats['avg_time'] * 1000:.2f}ms")
    print(f"  最快: {stats['min_time'] * 1000:.2f}ms | 最慢: {stats['max_time'] * 1000:.2f}ms")
    """
    📊 test_all 性能统计:
    调用次数: 10
    总耗时: 22492.76ms
    平均耗时: 2249.28ms
    最快: 1867.27ms | 最慢: 3059.87ms   
    """
