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
from config import HEADERS, BILIBILI_GUOCHUNAG

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


def _fetch_bilibili_guochuang_today() -> dict[str, list] | None:
    """从哔哩哔哩国创频道获取今日更新的动漫信息。"""
    html_path = "bilibili_guochuang.html"  # 临时 HTML 文件名
    try:
        logger.info("开始抓取哔哩哔哩国创频道每日更新信息...")  # 修正日志信息
        random_delay()

        session = requests.Session()
        session.headers.update(HEADERS)

        # 获取页面内容
        logger.info("正在获取国创动漫页面...")
        res = session.get(BILIBILI_GUOCHUNAG, timeout=15)
        res.raise_for_status()  # 对于不良响应（4xx 或 5xx）抛出 HTTPError

        # 保存 HTML 以便调试
        html_path = os.path.join(os.getcwd(), "bilibili_guochuang.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(res.text)
        logger.info(f"HTML 已保存到 {html_path}")

        # 解析 HTML
        soup = BeautifulSoup(res.text, "html.parser")

        # 获取今天的中文星期
        weekday = config.weekday
        result = {weekday: []}

        logger.info("正在查找今日更新模块...")

        # 查找时间线中所有今日更新的动漫
        today_groups = soup.select('.season-group.today:not(.season-timer)')
        logger.info(f"找到 {len(today_groups)} 个今日更新的动漫组")

        if not today_groups:
            logger.warning("未找到今日更新的动漫组")
            return result

        for group in today_groups:
            # 提取更新时间
            time_div = group.select_one('.group-time')
            if not time_div:
                continue
            update_time = time_div.get_text(strip=True)

            # 提取所有动漫条目
            items = group.select('.season-item')
            for item in items:
                # 提取主要信息
                data = {
                    "platform": "bilibili",
                    "title": None,
                    "update_count": None,
                    "update_info": None,
                    "image_url": None,
                    "detail_url": None,
                    "tagline": None,
                    "update_time": update_time,
                    "status": None
                }

                # 提取标题
                title_elem = item.select_one('.season-title')
                if title_elem:
                    data["title"] = clean_text(title_elem.get_text(strip=True))

                # 提取集数信息
                desc_elem = item.select_one('.season-desc')
                if desc_elem:
                    data["update_count"] = clean_text(desc_elem.get_text(strip=True))

                    # 确定更新状态
                    data["status"] = "已更新" if 'published' in desc_elem.get('class', []) else "即将更新"

                # 提取封面图片
                img_elem = item.select_one('img')
                if img_elem and img_elem.get('src'):
                    cover = img_elem['src']
                    if cover.startswith('//'):
                        cover = 'https:' + cover
                    data["image_url"] = cover

                # 提取详情链接
                link_elem = item.select_one('a[href]')
                if link_elem and link_elem.get('href'):
                    link = link_elem['href']
                    if link.startswith('//'):
                        link = 'https:' + link
                    data["detail_url"] = link

                # 添加到结果列表
                if data["title"]:
                    result[weekday].append(data)
                    logger.info(f"已添加: {data['title']} - {data['update_count']} ({data['status']})")

        return result

    except requests.exceptions.Timeout:
        logger.error("请求超时。将在 10 秒后重试...")
        time.sleep(10)
        return _fetch_bilibili_guochuang_today()  # 重试一次
    except requests.exceptions.TooManyRedirects:
        logger.error("重定向过多。请检查 URL。")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求错误: {str(e)}")
        return None
    except Exception as e:
        logger.exception(f"获取哔哩哔哩国创更新信息时发生意外错误: {str(e)}")
        return None
    finally:
        # 只有在文件存在时才删除
        if os.path.exists(html_path):
            try:
                os.remove(html_path)
                logger.info(f"已清理临时文件: {html_path}")
            except Exception as e:
                logger.error(f"删除临时文件时出错: {str(e)}")
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


def fetch_bilibili_guochuang_today() -> dict[str, list] | None:
    # 执行 5 次测试
    num_tests = 5
    for i in range(1, num_tests + 1):
        logger.info(f"\n{'=' * 40}")
        logger.info(f"测试 #{i}")
        logger.info(f"{'=' * 40}")

        today_updates = _fetch_bilibili_guochuang_today()

        if today_updates:
            print_results(today_updates)
            return today_updates
            # save_results(today_updates, f"tencent_cartoon_test_{i}.json")
        else:
            logger.warning("未能获取今日更新信息。")

        # 在测试之间添加较长延迟，除非是最后一次测试
        if i < num_tests:
            logger.info(f"\n等待 10 秒后进行下一次测试 (测试 #{i + 1})...")
            time.sleep(10)


if __name__ == "__main__":
    fetch_bilibili_guochuang_today()
    print("\n所有测试完成！")
