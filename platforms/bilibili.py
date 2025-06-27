import asyncio
import json
import logging
import time
import aiohttp
import requests
import utils
from common import Result, AbstractFetcher, Logger
from common.decorators import timer, retry_async, print_after_return_async, print_performance_metrics
from config import BILIBILI_GUOCHUANG_API, BILIBILI_ANIME_API
from utils import iso_date_ld
from utils import print_results, clean_text


# 配置日志
class BilibiliFetcher(AbstractFetcher):
    """哔哩哔哩数据抓取器，继承自抽象基类 AbstractFetcher。"""

    def __init__(self, api_url: str, platform: str = "bilibili"):
        super().__init__()
        self.api_url = api_url
        self.platform = platform

    def _build_result_from_episode(self, ep: dict) -> Result:
        super()._build_result_from_episode(ep)
        """从单个 episode 字典构建 Result 对象。"""
        pub_index = ep.get("pub_index", "").strip()
        count = utils.extract_number(pub_index)
        return Result(
            platform=self.platform,
            title=clean_text(ep.get("title", "")),
            update_count=str(count),
            update_info=f"更新至{pub_index}",
            image_url=ep.get("square_cover") or ep.get("cover"),
            detail_url=f"https://www.bilibili.com/bangumi/play/ep{ep.get('episode_id')}",
            update_time=iso_date_ld
        )

    @timer(unit="ms")
    async def _fetch_bilibili_update_today(self, session: aiohttp.ClientSession) -> dict[str, list] | None:
        """从哔哩哔哩国创频道官方 JSON 接口获取今日更新的动漫信息。"""
        try:
            await super().fetch_update_data(session)
            data = json.loads(self.response_text)
            logging.debug(f"解析从API获取到的 JSON 数据为：{data}")
            if data.get("code") != 0 or "result" not in data:
                logging.error("接口返回异常：%s", data)
                return None
            # 找到 is_today == 1 的那一天
            today_list = [d for d in data["result"] if d.get("is_today") == 1]
            if not today_list:
                logging.info("今日没有更新")
                return self.result
            # 取出今天的更新数据
            today = today_list[0]
            # 初始化结果字典
            for ep in (e for e in today.get("episodes") or [] if e.get("published") == 1):
                item = self._build_result_from_episode(ep)
                logging.info(f"识别到更新：{item.title} {item.update_info}")
                self.result[utils.weekday_today].append(item)

            return self.result

        except requests.exceptions.Timeout:
            logging.warning("请求超时，10 秒后重试...")
            time.sleep(10)
            return None
        except requests.exceptions.RequestException as e:
            logging.error("请求错误：%s", e)
            return None
        except Exception as e:
            logging.exception("未知错误：%s", e)
            return None

    @retry_async(
        retries=5,
        delay=10,
        retry_condition=lambda result: not result
    )
    @print_after_return_async(print_results, print_condition=lambda r: not r and any(r.values()))
    @timer(unit="ms")
    async def fetch_bilibili_cartoon_today(self) -> dict[str, list] | None:
        """获取哔哩哔哩国创频道今日更新的动漫信息。"""
        logging.info("开始获取哔哩哔哩动漫频道今日更新...")
        async with aiohttp.ClientSession() as session:
            return await self._fetch_bilibili_update_today(session)


@timer(enable_stats=True, print_report=False)
def test_all1():
    bilibili_guochuang = BilibiliFetcher(BILIBILI_GUOCHUANG_API)
    bilibili_anime = BilibiliFetcher(BILIBILI_ANIME_API)
    asyncio.run(bilibili_guochuang.fetch_bilibili_cartoon_today())
    asyncio.run(bilibili_anime.fetch_bilibili_cartoon_today())


@timer(enable_stats=True, print_report=False)
async def test_all2():
    bilibili_guochuang = BilibiliFetcher(BILIBILI_GUOCHUANG_API)
    bilibili_anime = BilibiliFetcher(BILIBILI_ANIME_API)
    t1 = asyncio.create_task(bilibili_guochuang.fetch_bilibili_cartoon_today())
    t2 = asyncio.create_task(bilibili_anime.fetch_bilibili_cartoon_today())
    # 等待所有任务完成
    await asyncio.gather(t1, t2)


if __name__ == "__main__":
    Logger.init(
        level=logging.DEBUG,
        max_bytes=10_000_000,
        backup_count=5,
        console=True,
        colored=True
    )

    # 多次调用
    for i in range(1, 11):
        asyncio.run(test_all2())
        # test_all1()

    # 获取统计信息
    # stats = test_all1.get_stats()
    print_performance_metrics(test_all2)
    """
    📊 test_all1 性能统计:
    调用次数: 10
    总耗时: 1762.63ms
    平均耗时: 176.26ms
    最快: 138.37ms | 最慢: 208.08ms
    
    📊 test_all2 性能统计:
    调用次数: 10
    总耗时: 1109.34ms
    平均耗时: 110.93ms
    最快: 92.30ms | 最慢: 136.00ms
    
    """
