import logging  # 导入 logging 模块
import os
import time
from urllib.parse import urljoin, unquote

import requests
from bs4 import BeautifulSoup

from common import Result
import config
from config import HEADERS, TENCENT_CARTOON_BASE_URL
from common.decorators import retry, print_after_return
from utils import print_results, extract_number, iso_date_ld, random_delay, clean_text

# 配置日志
logger = logging.getLogger(__name__)


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


def _fetch_qq_cartoon_today(api_url: str) -> dict[str, list]:
    """从腾讯视频动漫频道获取今日更新的动漫信息。"""
    html_path = "tencent_cartoon.html"  # 临时 HTML 文件名
    try:
        logger.info("开始抓取腾讯视频动漫频道每日更新信息...")
        random_delay()

        session = requests.Session()
        session.headers.update(HEADERS)

        # 获取页面内容
        logger.info("正在获取腾讯动漫页面...")
        res = session.get(api_url, timeout=15)
        res.raise_for_status()  # 对于不良响应（4xx 或 5xx）抛出 HTTPError

        # 保存 HTML 以便调试
        html_filename = "tencent_cartoon.html"
        html_path = os.path.join(os.getcwd(), html_filename)  # 使用 os.path.join 构造路径
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(res.text)
        logger.info(f"HTML 已保存到 {html_path}")

        # 解析 HTML
        soup = BeautifulSoup(res.text, "html.parser")

        # 获取今天的中文星期
        weekday = config.weekday
        result = {weekday: []}

        logger.info("正在查找今日更新模块...")

        # 查找所有包含动漫项目的容器
        banner_wraps = soup.find_all('div', class_='form-banner-item-wrap')
        logger.info(f"找到 {len(banner_wraps)} 个动漫容器")

        for wrap in banner_wraps:
            # 每个容器内有多个项目，但只取第一个实际显示的项目
            video_items = wrap.find_all('div', class_='video-banner-item')

            for item in video_items:
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

                # 添加到结果列表
                if data["title"]:
                    result[weekday].append(data)
                    logger.info(f"识别到更新：{data.title} {data.update_info}")

        return result

    except requests.exceptions.Timeout:
        logger.error("请求超时。将在 10 秒后重试...")
        time.sleep(10)
        return _fetch_qq_cartoon_today()  # 重试一次
    except requests.exceptions.TooManyRedirects:
        logger.error("重定向过多。请检查 URL。")
        return {}
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求错误: {str(e)}")
        return {}
    except Exception as e:
        logger.exception(f"获取腾讯动漫更新信息时发生意外错误: {str(e)}")
        return {}
    finally:
        os.remove(html_path)  # 清理临时 HTML 文件
        random_delay()


@retry(
    retries=5,
    delay=10,
    retry_condition=lambda result: not any(result.values())
)
@print_after_return(print_results, print_condition=lambda r: any(r.values()))
# @save_after_return(filename="qq_cartoon_today.json", save_condition=lambda r: any(r.values()))
def fetch_qq_cartoon_today() -> dict[str, list] | None:
    """获取腾讯视频动漫频道今日更新的动漫信息。"""
    logger.info("开始获取腾讯视频动漫频道今日更新...")
    return _fetch_qq_cartoon_today(TENCENT_CARTOON_BASE_URL)


if __name__ == "__main__":
    fetch_qq_cartoon_today()
    print("\n所有测试完成！")
