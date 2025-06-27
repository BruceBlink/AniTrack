import asyncio
import logging  # 导入 logging 模块
import os
import time
from urllib.parse import urljoin, unquote
import aiohttp
import requests
from bs4 import BeautifulSoup, Tag
import utils
from common import Result, AbstractFetcher, Logger
from common.decorators import timer, retry_async, print_after_return_async, \
    print_performance_metrics
from config import TENCENT_CARTOON_BASE_URL
from utils import print_results, extract_number, iso_date_ld, clean_text


class TencentFetcher(AbstractFetcher):
    def __init__(self, api_url: str, platform: str = "tencent"):
        super().__init__()
        self.api_url = api_url
        self.platform = platform

    def _build_result_from_episode(self, item: dict | Tag) -> Result:
        super()._build_result_from_episode(item)
        data = Result(
            platform="tencent",
            title="",
            update_count="",
            update_info="",
            image_url="",
            detail_url="",
            update_time=iso_date_ld
        )
        # 提取标题
        title_elem = item.select_one('.banner-title')
        if title_elem:
            data["title"] = clean_text(title_elem.get_text(strip=True))

        # 提取更新集数
        update_count_elem = item.select_one('.corner-mark--rightBottom')
        if update_count_elem:
            data["update_count"] = extract_number(clean_text(update_count_elem.get_text(strip=True)))

        # 提取更新说明
        update_info_elem = item.select_one('.banner-subtitle')
        if update_info_elem:
            data["update_info"] = clean_text(update_info_elem.get_text(strip=True))

        # 提取封面图片
        img_elem = item.select_one('.banner-cover')
        if img_elem:
            img_url = img_elem.get('data-src') or img_elem.get('src')
            if img_url:
                data["image_url"] = normalize_url(img_url)

        # 提取详情链接
        link_elem = item.select_one('.banner-cover-wrap')
        if link_elem and link_elem.get('href'):
            data["detail_url"] = normalize_url(link_elem['href'])

        # 提取宣传语
        tagline_elem = item.select_one('.tag-wrap span')
        if tagline_elem:
            data["tagline"] = clean_text(tagline_elem.get_text(strip=True))

        # 提取平台信息
        platform_elem = item.select_one('.corner-mark--rightTop')
        if platform_elem:
            data["platform"] = data["platform"] + clean_text(platform_elem.get_text(strip=True))

        # 提取元数据参数
        dt_params = item.get('dt-params', '')
        if dt_params:
            params = {}
            for pair in dt_params.split('&'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    params[key] = unquote(value)

            data["metadata"] = params
        return data

    async def _fetch_qq_cartoon_today(self, session: aiohttp.ClientSession) -> dict[str, list] | None:
        """从腾讯视频动漫频道获取今日更新的动漫信息。"""
        try:
            await super().fetch_update_data(session)
            # 解析 HTML
            soup = BeautifulSoup(self.response_text, "html.parser")
            logging.debug(f"解析从API获取到的 HTML 内容为：{soup.prettify()}...")
            # 获取今天的中文星期
            weekday = utils.weekday_today

            logging.info("正在查找今日更新模块...")

            # 查找所有包含动漫项目的容器
            banner_wraps = soup.find_all('div', class_='form-banner-item-wrap')
            if not len(banner_wraps):
                logging.warning("没有找到任何动漫更新信息，可能页面结构已更改或没有今日更新。")
                return None
            for wrap in banner_wraps:
                # 每个容器内有多个项目，但只取第一个实际显示的项目
                video_items = wrap.find_all('div', class_='video-banner-item')

                for item in video_items:
                    data = self._build_result_from_episode(item)
                    # 添加到结果列表
                    if data["title"]:
                        self.result[weekday].append(data)
                        logging.info(f"识别到更新：{data.title} {data.update_info}")

            return self.result

        except requests.exceptions.Timeout:
            logging.error("请求超时。将在 10 秒后重试...")
            time.sleep(10)
        except requests.exceptions.TooManyRedirects:
            logging.error("重定向过多。请检查 URL。")
        except requests.exceptions.RequestException as e:
            logging.error(f"网络请求错误: {str(e)}")
        except Exception as e:
            logging.exception(f"获取腾讯动漫更新信息时发生意外错误: {str(e)}")

        return None

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


def normalize_url(url, base_url="https://v.qq.com"):
    """将给定 URL 规范化为绝对路径。"""
    if not url:
        return ""

    if url.startswith('//'):
        return 'https:' + url
    elif url.startswith('/'):
        return urljoin(base_url, url)
    elif not url.startswith('http'):
        # 处理 URL 可能是相对路径但不是以 / 开头的情况
        return urljoin(base_url, url)
    return url


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
    for i in range(0, 10):
        asyncio.run(test_all())

    print_performance_metrics(test_all)
