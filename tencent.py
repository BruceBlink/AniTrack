import json
import logging  # 导入 logging 模块
import os
import random
import re
import time
from urllib.parse import urljoin, unquote

import requests
from bs4 import BeautifulSoup

import config
from config import HEADERS, CARTOON_BASE_URL

# 配置日志
logger = logging.getLogger(__name__)


def random_delay(min_sec=1.2, max_sec=4.5):
    """引入随机延迟，模拟人类行为并避免被封锁。"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    logger.debug(f"延迟了 {delay:.2f} 秒。")


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


def clean_text(text):
    """清理文本，替换 HTML 实体并规范化空白字符。"""
    if not text:
        return ""

    # 替换常见的 HTML 实体
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&#x27;', "'", text)  # 撇号

    # 将所有空白字符（空格、制表符、换行符）规范化为单个空格，然后去除首尾空格。
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_qq_cartoon_today():
    """从腾讯视频动漫频道获取今日更新的动漫信息。"""
    try:
        logger.info("开始抓取腾讯视频动漫频道每日更新信息...")
        random_delay()

        session = requests.Session()
        session.headers.update(HEADERS)

        # 获取页面内容
        logger.info("正在获取腾讯动漫页面...")
        res = session.get(CARTOON_BASE_URL, timeout=15)
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
                # 提取主要信息
                data = {
                    "platform": "tencent",
                    "title": None,
                    "update_count": None,
                    "update_info": None,
                    "image_url": None,
                    "detail_url": None,
                    "tagline": None,
                    "metadata": {}
                }

                # 提取标题
                title_elem = item.select_one('.banner-title')
                if title_elem:
                    data["title"] = clean_text(title_elem.get_text(strip=True))

                # 提取更新集数
                update_count_elem = item.select_one('.corner-mark--rightBottom')
                if update_count_elem:
                    data["update_count"] = clean_text(update_count_elem.get_text(strip=True))

                # 提取更新说明
                update_info_elem = item.select_one('.banner-subtitle')
                if update_info_elem:
                    data["update_info"] = clean_text(update_info_elem.get_text(strip=True))

                # 提取封面图片
                img_elem = item.select_one('.banner-cover')
                if img_elem:
                    img_url = img_elem.get('data-src') or img_elem.get('src')
                    if img_url:
                        data["image"] = normalize_url(img_url)

                # 提取详情链接
                link_elem = item.select_one('.banner-cover-wrap')
                if link_elem and link_elem.get('href'):
                    data["link"] = normalize_url(link_elem['href'])

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
                    logger.info(f"已添加: {data['title']}")

        return result

    except requests.exceptions.Timeout:
        logger.error("请求超时。将在 10 秒后重试...")
        time.sleep(10)
        return fetch_qq_cartoon_today()  # 重试一次
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
        random_delay()


def save_results(results, filename="tencent_cartoon.json"):
    """将结果保存到 JSON 文件。"""
    if not results:
        logger.info("没有可保存的结果。")
        return

    file_path = os.path.join(os.getcwd(), filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logger.info(f"结果已保存到 {file_path}")


def print_results(results):
    """将获取到的动漫更新结果打印到控制台。"""
    if not results:
        logger.info("没有找到任何更新信息可供打印。")
        return

    weekday = list(results.keys())[0]
    if not results[weekday]:
        logger.info(f"{weekday} 没有找到更新的动漫。")
        return

    print(f"\n{weekday} 更新动漫列表:")
    print("=" * 80)

    for i, anime in enumerate(results[weekday], 1):
        print(f"{i}. {anime['title']}")
        print(f"   更新集数: {anime['update_count']}")
        if anime['update_info'] and anime['update_info'] != anime['update_count']:  # 避免冗余
            print(f"   更新说明: {anime['update_info']}")
        if anime['image']:
            print(f"   封面图片: {anime['image']}")
        if anime['link']:
            print(f"   详情链接: {anime['link']}")
        print("-" * 80)

    print(f"\n统计: 共找到 {len(results[weekday])} 部今日更新的动漫")


if __name__ == "__main__":
    # 执行 5 次测试
    num_tests = 5
    for i in range(1, num_tests + 1):
        print(f"\n{'=' * 40}")
        print(f"测试 #{i}")
        print(f"{'=' * 40}")

        today_updates = fetch_qq_cartoon_today()

        if today_updates:
            print_results(today_updates)
            save_results(today_updates, f"tencent_cartoon_test_{i}.json")
        else:
            logger.warning("未能获取今日更新信息。")

        # 在测试之间添加较长延迟，除非是最后一次测试
        if i < num_tests:
            logger.info(f"\n等待 10 秒后进行下一次测试 (测试 #{i + 1})...")
            time.sleep(10)

    print("\n所有测试完成！")
