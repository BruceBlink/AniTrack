import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag
import utils
from common import Result, AbstractFetcher
from common.decorators import retry, print_after_return
from config import MIKANANI_BASE_URL
from utils import iso_date_ld, print_results


class MikananiFetcher(AbstractFetcher):
    """蜜柑计划数据抓取器，继承自抽象基类 AbstractFetcher。"""

    def __init__(self, api_url: str = MIKANANI_BASE_URL, platform: str = "Mikanani"):
        super().__init__()
        self.api_url = api_url
        self.platform = platform

    def send_request(self):
        """实现数据抓取逻辑，获取蜜柑计划今日更新的动漫信息。"""
        super().send_request()

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

    def _fetch_mikanani_update_today(self) -> dict[str, list] | None:
        """抓取 Mikanani 今日更新的番剧数据。"""
        self.logger.info("Fetching today's Mikanani data...")

        try:
            super().send_request()
            soup = BeautifulSoup(self.response.text, 'html.parser')
            self.logger.debug(f"解析 HTML 内容：{soup}")

            items = (li for li in soup.find_all("li") if li.find("div", class_="num-node text-center"))

            for li in items:
                anime_info = self._build_result_from_episode(li)
                self.logger.info(f"识别到更新：{anime_info.title} - {anime_info.update_info}")
                self.result[utils.weekday_today].append(anime_info)

            return self.result
        except requests.exceptions.Timeout:
            self.logger.warning("请求超时，10 秒后重试...")
            time.sleep(10)
            return self._fetch_mikanani_update_today()
        except requests.RequestException as e:
            self.logger.error(f"请求处理异常：{e}")
            return None
        except Exception as e:
            self.logger.exception(f"其他错误：{e}")
            return None

    @retry(
        retries=5,
        delay=10,
        retry_condition=lambda result: not result
    )
    @print_after_return(print_results, print_condition=lambda r: any(r.values()))
    # @save_after_return(filename="qq_cartoon_today.json", save_condition=lambda r: any(r.values()))
    def fetch_mikanani_update_today(self) -> dict[str, list] | None:
        """获取蜜柑计划今日更新的动漫信息。"""
        self.logger.info("开始获取蜜柑计划今日更新...")
        return self._fetch_mikanani_update_today()


if __name__ == "__main__":
    mikanani_fetcher = MikananiFetcher(api_url=MIKANANI_BASE_URL)
    print(mikanani_fetcher.fetch_mikanani_update_today())
    print("\n所有测试完成！")
