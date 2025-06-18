import json
import logging  # 导入 logging 模块
import os

import requests
from bs4 import BeautifulSoup

import utils
from common import Result, HEADERS, retry, print_after_return
from config import YOUKU_COMICS_API
from utils import print_results

# 配置日志
logger = logging.getLogger(__name__)


def _fetch_youku_cartoon_today(api_url: str) -> dict[str, list] | None:
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
        logger.info(f"开始抓取优酷动漫频道每日更新信息...")
        utils.random_delay()  # 调用随机延迟函数

        with requests.Session() as session:
            session.headers.update(HEADERS)  # 更新会话头
            logger.info(f"正在请求页面: {api_url}")
            response = session.get(api_url, timeout=15)
            response.raise_for_status()  # 对 4xx/5xx 状态码抛出异常

            # 保存 HTML 以便调试
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            logger.info(f"HTML 已保存到 {html_path}")

            # 初始化结果字典
            weekday = utils.weekday_today
            result_data = {weekday: []}

            logger.info("正在解析 HTML 并提取 __INITIAL_DATA__...")
            soup = BeautifulSoup(response.text, "html.parser")

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
            # 视频地址需要vid +
            # https://v.youku.com/video?vid=XNjQ3MjQzMjE2MA==&scm=20140719.apircmd.298496.video_XNjQ3MjQzMjE2MA==
            # 解析 JSON 数据
            data = json.loads(fixed_json_str)
            module_list = data.get("moduleList", [])

            logger.info("正在通过生成器表达式提取今日更新漫画...")
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

            # 步骤4: 根据过滤后的 item 创建 Result 对象，并收集到列表中
            comics_found = [
                Result(
                    platform='youku',
                    title=item.get('title', '').strip(),
                    update_count=str(utils.extract_number(item.get('lbTexts', ''))),
                    update_info=item.get('lbTexts', '').strip(),
                    image_url=item.get('img', '').strip(),
                    detail_url="",
                    update_time=utils.iso_date_ld,
                )
                for item in updated_items
            ]
            result_data[weekday] = comics_found
            logger.info(f"成功提取到 {len(comics_found)} 部今日更新的漫画。")
            return result_data  # 成功获取并返回数据

    except requests.exceptions.Timeout:
        logger.warning("请求优酷动漫频道超时。")
    except requests.exceptions.HTTPError as e:
        logger.error(f"请求优酷动漫频道 HTTP 错误: {e.response.status_code} - {e.response.reason}")
        if e.response.status_code == 404:
            logger.error("URL 可能已失效。")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"连接到优酷动漫频道时出错: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求通用错误: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"解析 JSON 数据时出错: {e}")
        # 为了调试，可以打印部分引起错误的JSON字符串
        # logger.debug(f"原始 JSON 字符串（部分）: {fixed_json_str[:500]}...")
    except ValueError as e:
        logger.error(f"数据提取或逻辑错误: {e}")
    except Exception as e:
        logger.exception(f"获取优酷动漫频道更新信息时发生意外错误 {e}。")  # 记录完整的异常信息

    finally:
        # 无论成功或失败，尝试删除临时 HTML 文件
        if os.path.exists(html_path):
            try:
                os.remove(html_path)
                logger.info(f"已清理临时 HTML 文件: {html_path}")
            except OSError as e:
                logger.warning(f"清理临时文件失败: {e}")
        utils.random_delay()  # 每次尝试结束后都添加延迟

    return None  # 发生任何异常，返回 None


@retry(
    retries=5,
    delay=10,
    retry_condition=lambda result: not any(result.values())
)
@print_after_return(print_results, print_condition=lambda r: any(r.values()))
# @save_after_return(filename="qq_cartoon_today.json", save_condition=lambda r: any(r.values()))
def fetch_youku_cartoon_today() -> dict[str, list] | None:
    logger.info("开始获取优酷动漫频道今日更新...")
    return _fetch_youku_cartoon_today(YOUKU_COMICS_API)


if __name__ == "__main__":
    print(fetch_youku_cartoon_today())
    print("\n所有测试完成！")
