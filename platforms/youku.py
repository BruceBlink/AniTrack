import asyncio
import json
import logging  # 导入 logging 模块
import os
import aiohttp
import requests
from bs4 import BeautifulSoup, Tag
import utils
from common import Result, AbstractFetcher, Logger
from common.decorators import print_after_return_async, retry_async, timer, print_performance_metrics
from config import YOUKU_COMICS_API
from utils import print_results


class YoukuFetcher(AbstractFetcher):
    def __init__(self, api_url: str = YOUKU_COMICS_API, platform: str = "youku"):
        super().__init__()
        self.api_url = api_url
        self.platform = platform

    def _build_result_from_episode(self, item: dict | Tag) -> Result:
        super()._build_result_from_episode(item)
        return Result(
            platform=self.platform,
            title=item.get('title', '').strip(),
            update_count=str(utils.extract_number(item.get('lbTexts', ''))),
            update_info=item.get('lbTexts', '').strip(),
            image_url=item.get('img', '').strip(),
            detail_url=YOUKU_COMICS_API,
            update_time=utils.iso_date_ld,
        )

    async def _fetch_youku_cartoon_today(self, session: aiohttp.ClientSession) -> dict[str, list] | None:
        """
        从优酷动漫频道一次性获取今日更新的动漫信息。
        此函数不包含重试逻辑，失败即返回 None。

        Args:
            api_url: 优酷动漫频道的API URL。

        Returns:
            包含每日更新动漫信息的字典，如果获取失败则返回 None。
        """
        html_file_name = "youku_cartoon.html"  # 临时 HTML 文件名
        html_path = os.path.join(os.getcwd(), html_file_name)  # 完整的临时文件路径

        try:
            await super().fetch_update_data(session)
            # 保存 HTML 以便调试
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(self.response_text)
            logging.info(f"HTML 已保存到 {html_path}")

            # 初始化结果字典
            weekday = utils.weekday_today

            logging.info("正在解析 HTML 并提取 __INITIAL_DATA__...")
            soup = BeautifulSoup(self.response_text, "html.parser")

            # 查找包含 JavaScript 变量 __INITIAL_DATA__ 的 <script> 标签
            script_content = None
            for tag in soup.find_all("script"):
                if tag.string and "__INITIAL_DATA__" in tag.string:
                    script_content = tag.string
                    break

            if not script_content:
                raise ValueError("未找到包含 window.__INITIAL_DATA__ 的 <script> 标签。")

            # 提取并清理 JSON 字符串
            prefix = "window.__INITIAL_DATA__="
            json_str = script_content[len(prefix) + 1:].strip().rstrip(";")
            fixed_json_str = json_str.replace('undefined', 'null')
            # 解析 JSON 数据
            data = json.loads(fixed_json_str)
            module_list = data.get("moduleList", [])

            logging.info("正在通过生成器表达式提取今日更新漫画...")
            # --- 优化后的四层循环逻辑 ---
            # 步骤1: 找到所有 title 为 '每日更新' 的 component
            daily_update_components = (
                comp
                for card_mod in module_list
                for comp in card_mod.get('components', [])
                if comp.get('title') == '每日更新'
            )

            # 步骤2: 从这些 component 中提取所有 item，并扁平化
            all_raw_items = (
                item
                for comp in daily_update_components
                for sublist in comp.get('itemList', [])
                for item in sublist
            )

            # 步骤3: 过滤出 updateTips 为 '有更新' 的 item
            updated_items = (
                item for item in all_raw_items if item.get('updateTips') == '有更新'
            )

            # updated_items = [item for item in all_raw_items if item.get('updateTips') == '有更新']
            # 步骤4: 根据过滤后的 item 创建 Result 对象，并收集到列表中
            comics_found = list({  # 去重处理
                self._build_result_from_episode(item)
                for item in updated_items
            })
            for comic in comics_found:
                logging.info(f"识别到更新：{comic.title} {comic.update_info}")
            self.result[weekday] = comics_found  # 将结果存入字典
            logging.info(f"成功提取到 {len(comics_found)} 部今日更新的动漫。")
            return self.result  # 成功获取并返回数据

        except requests.exceptions.Timeout:
            logging.warning("请求优酷动漫频道超时。")
        except requests.exceptions.HTTPError as e:
            logging.error(f"请求优酷动漫频道 HTTP 错误: {e.response.status_code} - {e.response.reason}")
            if e.response.status_code == 404:
                logging.error("URL 可能已失效。")
        except requests.exceptions.ConnectionError as e:
            logging.error(f"连接到优酷动漫频道时出错: {e}")
        except requests.exceptions.RequestException as e:
            logging.error(f"网络请求通用错误: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"解析 JSON 数据时出错: {e}")
            # 为了调试，可以打印部分引起错误的JSON字符串
            # logger.debug(f"原始 JSON 字符串（部分）: {fixed_json_str[:500]}...")
        except ValueError as e:
            logging.error(f"数据提取或逻辑错误: {e}")
        except Exception as e:
            logging.exception(f"获取优酷动漫频道更新信息时发生意外错误 {e}。")  # 记录完整的异常信息

        finally:
            # 无论成功或失败，尝试删除临时 HTML 文件
            if os.path.exists(html_path):
                try:
                    os.remove(html_path)
                    logging.info(f"已清理临时 HTML 文件: {html_path}")
                except OSError as e:
                    logging.warning(f"清理临时文件失败: {e}")

        return None  # 发生任何异常，返回 None

    @retry_async(
        retries=5,
        delay=10,
        retry_condition=lambda result: not result
    )
    @print_after_return_async(print_results, print_condition=lambda r: any(r.values()))
    @timer(unit="ms")
    async def fetch_youku_cartoon_today(self) -> dict[str, list] | None:
        logging.info("开始获取优酷动漫频道今日更新...")
        async with aiohttp.ClientSession() as session:
            return await self._fetch_youku_cartoon_today(session)


def _get_video_id(preview_info: dict) -> str:
    """ 从预览信息中提取视频 ID"""

    return preview_info.get("videoId", "").strip() if preview_info else ""


def _get_youku_video_url(item: dict) -> str:
    """ 根据 item 中的 previewInfo 和 vid scm spm提取视频 URL。"""
    'https://v.youku.com/v_show/id_XNjM5NTIzOTM2MA==.html?scm=20140719.apircmd.298639.video_XNjM5NTIzOTM2MA%3D%3D&s=badbb5792f934ddb82fd'
    'https://v.youku.com/video?vid=XNjQ1NTg1OTE2MA==&scm=20140719.manual.feed.show_badbb5792f934ddb82fd&spm=a2hkl.14919748_WEBCOMIC_JINGXUAN.calendar_scroll_1.d_1_play'
    preview_info: dict = item.get('previewInfo', {})
    vid = _get_video_id(preview_info)
    scm = item.get('scm', '').strip()
    'https://v.youku.com/v_show/id_XNjQ1NDcyMjAxMg==.html'

    spm = f'{item.get('spmAB', '').strip()}.{item.get('spmC', '').strip()}.{item.get('spmD', '').strip()}'.strip()
    return f'https://v.youku.com/video?vid={vid}&scm={scm}&spm={spm}' if vid and scm else YOUKU_COMICS_API


@timer(enable_stats=True, print_report=False)
async def test_all():
    mikanani_fetcher = YoukuFetcher(api_url=YOUKU_COMICS_API)
    t1 = asyncio.create_task(mikanani_fetcher.fetch_youku_cartoon_today())
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
