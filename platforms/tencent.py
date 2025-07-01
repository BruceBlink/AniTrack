import asyncio
import json
import logging  # 导入 logging 模块
import aiohttp
from bs4 import BeautifulSoup, Tag
import utils
from common import Result, AbstractFetcher, Logger
from common.decorators import timer, retry_async, print_after_return_async, \
    print_performance_metrics
from config import TENCENT_CARTOON_BASE_URL
from utils import print_results


def _extract_vikor_json(html: str) -> dict:
    """从 HTML 中提取并解析 window.__vikor__context__ 对应的 JSON."""
    soup = BeautifulSoup(html, "html.parser")
    logging.debug("解析 HTML 内容：\n%s", soup.prettify())

    script = next(
        (tag.string for tag in soup.find_all("script")
         if tag.string and "window.__vikor__context__" in tag.string),
        None
    )
    if not script:
        raise ValueError("未找到包含 window.__vikor__context__ 的 <script> 标签。")

    # 分割出真正的 JSON 串，并替换 undefined
    prefix = "window.__vikor__context__="
    try:
        raw_json = script.split(prefix, 1)[1].rstrip(";")
    except IndexError:
        raise ValueError("脚本内容格式不正确，无法提取 JSON。")

    fixed_json = raw_json.replace("undefined", "null")
    return json.loads(fixed_json)


def _find_daily_card(pinia_state: dict) -> dict:
    """从 _piniaState 中找到 moduleTitle 为 '每日更新' 的 card."""
    cards = (
        pinia_state
        .get("channelPageData", {})
        .get("channelsModulesMap", {})
        .get("100119", {})
        .get("cardListData", [])
    )
    return next((c for c in cards if c.get("moduleTitle") == "每日更新"), {})


def _get_qq_video_url(cid: str) -> str:
    """从预览信息中提取视频 ID"""
    return f"https://v.qq.com/x/cover/{cid}.html"


class TencentFetcher(AbstractFetcher):
    def __init__(self, api_url: str = TENCENT_CARTOON_BASE_URL, platform: str = "tencent"):
        super().__init__()
        self.api_url = api_url
        self.platform = platform

    def _build_result_from_episode(self, item: dict | Tag) -> Result:
        super()._build_result_from_episode(item)
        uniImgTag = item.get("uniImgTag", "")
        update_info = json.loads(uniImgTag)
        update_count = update_info.get("tag_4", "").get("text", "")
        cid = item.get("cid", "")
        return Result(
            platform=self.platform,
            title=item.get('title', '').strip(),
            update_count=str(utils.extract_number(update_count)),
            update_info=item.get('topicLabel', '').strip(),
            image_url=item.get('coverPic', '').strip(),
            detail_url=_get_qq_video_url(cid),
            update_time=utils.iso_date_ld,
        )

    async def _fetch_qq_cartoon_today(self, session: aiohttp.ClientSession) -> dict[str, list] | None:
        """从腾讯视频动漫频道获取今日更新的动漫信息。"""

        await super().fetch_update_data(session)
        # 解析 HTML
        # 1. 解析 JSON
        data = _extract_vikor_json(self.response_text)
        pinia = data.get("_piniaState", {})

        # 2. 找到“每日更新”模块
        daily = _find_daily_card(pinia)
        if not daily:
            logging.warning("未找到“每日更新”模块，返回空结果。")
            return None

            # 3. 提取今日更新的视频列表
        tab_id = daily.get("selectedTabId", "")
        today_videos = (
            daily
            .get("videoBannerMap", {})
            .get(tab_id, {})
            .get("videoList", [])
        )

        # 4. 构建结果并记录日志
        comics = [self._build_result_from_episode(item) for item in today_videos]
        for comic in comics:
            logging.info(f"识别到更新：{comic.title}, {comic.update_info}")

        # 5. 存储并返回
        weekday = utils.weekday_today
        self.result[weekday] = comics
        logging.info(f"成功提取到 {len(comics)}部今日更新的动漫。")
        return self.result

    @retry_async(
        retries=5,
        delay=10,
        retry_condition=lambda result: not result
    )
    @print_after_return_async(print_results, print_condition=lambda r: not r)
    @timer(unit="ms")
    async def fetch_qq_cartoon_today(self) -> dict[str, list] | None:
        """获取腾讯视频动漫频道今日更新的动漫信息。"""
        logging.info("开始获取腾讯视频动漫频道今日更新...")
        async with aiohttp.ClientSession() as session:
            return await self._fetch_qq_cartoon_today(session)


@timer(enable_stats=True, print_report=False)
async def test_all():
    tencent_fetcher = TencentFetcher(api_url=TENCENT_CARTOON_BASE_URL)
    t1 = asyncio.create_task(tencent_fetcher.fetch_qq_cartoon_today())
    return await asyncio.gather(t1)


if __name__ == "__main__":
    Logger.init(
        level=logging.DEBUG,
        max_bytes=10_000_000,
        backup_count=5,
        console=True,
        colored=True
    )
    # for i in range(0, 10):
    asyncio.run(test_all())

    print_performance_metrics(test_all)
