import asyncio
import logging
import aiohttp
import requests
from bs4 import BeautifulSoup, Tag
import utils
from common import Result, AbstractFetcher, Logger
from common.decorators import retry_async, print_after_return_async, timer, print_performance_metrics
from config.config import AGE_CARTOON_API
from utils import iso_date_ld, print_results


class AgedmFetcher(AbstractFetcher):
    """AGE动漫数据抓取器，继承自抽象基类 AbstractFetcher。"""

    def __init__(self, api_url: str = AGE_CARTOON_API, platform: str = "agedm"):
        super().__init__()
        self.api_url = api_url
        self.platform = platform

    def _build_result_from_episode(self, item: Tag) -> Result:
        super()._build_result_from_episode(item)
        """从单个 <item> 元素构建 Result 对象。"""
        title_tag = item.select_one('.video_item-title a')
        info_tag  = item.select_one('.video_item--info')
        img_tag   = item.select_one('img.video_thumbs')

        return Result(
            platform=self.platform,
            title=title_tag.get_text(strip=True),
            update_count=str(utils.extract_number(info_tag.get_text(strip=True))),
            update_info="",
            image_url=img_tag['data-original'],
            detail_url=title_tag['href'],
            update_time=iso_date_ld,
        )

    async def _fetch_agedm_update_today(self, session: aiohttp.ClientSession) -> dict[str, list] | None:
        """抓取 agedm 今日更新的番剧数据。"""
        try:
            await super().fetch_update_data(session)
            soup = BeautifulSoup(self.response_text, 'html.parser')
            logging.debug(f"解析从API获取到的 HTML 内容为：{soup.prettify()}...")
            video_list = soup.find_all("div", class_="video_list_box recent_update mb-3 pb-3")
            # 获取今日更新的番剧列表
            today_update = video_list[0] if video_list else None

            items = today_update.select("div.video_item")
            for item in items:
                anime_info = self._build_result_from_episode(item)
                logging.info(f"识别到更新：{anime_info.title} {anime_info.update_info}")
                self.result[utils.weekday_today].append(anime_info)

            return self.result
        except requests.exceptions.Timeout:
            logging.warning("请求超时，10 秒后重试...")
        except requests.RequestException as e:
            logging.error(f"请求处理异常：{e}")
        except Exception as e:
            logging.exception(f"其他错误：{e}")
        return None

    @retry_async(
        retries=5,
        delay=10,
        retry_condition=lambda result: not result
    )
    @print_after_return_async(print_results, print_condition=lambda r: not r and any(r.values()))
    @timer(unit="ms")
    async def fetch_agedm_update_today(self) -> dict[str, list] | None:
        """获取AGE动漫今日更新的动漫信息。"""
        logging.info("开始获AGE动漫今日更新...")
        async with aiohttp.ClientSession() as session:
            return await self._fetch_agedm_update_today(session)


@timer(enable_stats=True, print_report=False)
async def test_all():
    agedm_fetcher = AgedmFetcher()
    t1 = asyncio.create_task(agedm_fetcher.fetch_agedm_update_today())
    return await asyncio.gather(t1)


if __name__ == "__main__":
    Logger.init(
        level=logging.DEBUG,
        max_bytes=10_000_000,
        backup_count=5,
        console=True,
        colored=True
    )

    # for i in range(1, 11):
    asyncio.run(test_all())
    # 获取统计信息
    print_performance_metrics(test_all)
    """
    📊 test_all 性能统计:
    调用次数: 10
    总耗时: 22492.76ms
    平均耗时: 2249.28ms
    最快: 1867.27ms | 最慢: 3059.87ms   
    """
