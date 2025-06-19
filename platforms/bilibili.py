import time

import requests

import utils
from common import Result, AbstractFetcher
from common.decorators import retry, print_after_return
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

    def send_request(self):
        """实现数据抓取逻辑，获取哔哩哔哩国创频道今日更新的动漫信息。"""
        super().send_request()

    def _build_result_from_episode(self, ep: dict) -> Result:
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

    def _fetch_bilibili_update_today(self) -> dict[str, list] | None:
        """从哔哩哔哩国创频道官方 JSON 接口获取今日更新的动漫信息。"""
        try:
            self.send_request()
            data = self.response.json()
            if data.get("code") != 0 or "result" not in data:
                self.logger.error("接口返回异常：%s", data)
                return None
            self.logger.info(f"成功获取哔哩哔哩更新时间线数据{data}。")
            # 找到 is_today == 1 的那一天
            today_list = [d for d in data["result"] if d.get("is_today") == 1]
            if not today_list:
                self.logger.info("今日没有更新")
                return self.result
            # 取出今天的更新数据
            today = today_list[0]
            # 初始化结果字典
            for ep in (e for e in today.get("episodes") or [] if e.get("published") == 1):
                item = self._build_result_from_episode(ep)
                self.logger.info("识别到更新：%s %s", item.title, item.update_info)
                self.result[utils.weekday_today].append(item)

            return self.result

        except requests.exceptions.Timeout:
            self.logger.warning("请求超时，10 秒后重试...")
            time.sleep(10)
            return self._fetch_bilibili_update_today()
        except requests.exceptions.RequestException as e:
            self.logger.error("请求错误：%s", e)
            return None
        except Exception as e:
            self.logger.exception("未知错误：%s", e)
            return None

    @retry(
        retries=5,
        delay=10,
        retry_condition=lambda result: not result
    )
    @print_after_return(print_results, print_condition=lambda r: any(r.values()))
    # @save_after_return(filename="bilibili_guochuang_today.json", save_condition=lambda r: any(r.values()))
    def fetch_bilibili_cartoon_today(self) -> dict[str, list] | None:
        """获取哔哩哔哩国创频道今日更新的动漫信息。"""
        self.logger.info("开始获取哔哩哔哩动漫频道今日更新...")
        return self._fetch_bilibili_update_today()


if __name__ == "__main__":
    bilibili_guochuang = BilibiliFetcher(BILIBILI_GUOCHUANG_API)

    bilibili_guochuang_data = bilibili_guochuang.fetch_bilibili_cartoon_today()

    bilibili_anime = BilibiliFetcher(BILIBILI_ANIME_API)
    bilibili_anime_data = bilibili_anime.fetch_bilibili_cartoon_today()
    print("\n所有测试完成！")
