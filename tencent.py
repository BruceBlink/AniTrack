import requests
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from datetime import datetime
import re
import time
import random
import os
import logging  # 导入 logging 模块

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 "
                  "Safari/537.36 Edg/125.0.0.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://v.qq.com/",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Ch-Ua": '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
}

CARTOON_BASE_URL = "https://v.qq.com/channel/cartoon"


def random_delay(min_sec=1.2, max_sec=4.5):
    """引入随机延迟，模拟人类行为并避免被封锁。"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    logging.debug(f"延迟了 {delay:.2f} 秒。")


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
        logging.info("开始抓取腾讯视频动漫频道每日更新信息...")
        random_delay()

        session = requests.Session()
        session.headers.update(HEADERS)

        # 获取页面内容
        logging.info("正在获取腾讯动漫页面...")
        res = session.get(CARTOON_BASE_URL, timeout=15)
        res.raise_for_status()  # 对于不良响应（4xx 或 5xx）抛出 HTTPError

        # 保存 HTML 以便调试
        html_filename = "tencent_cartoon.html"
        html_path = os.path.join(os.getcwd(), html_filename)  # 使用 os.path.join 构造路径
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(res.text)
        logging.info(f"HTML 已保存到 {html_path}")

        # 解析 HTML
        soup = BeautifulSoup(res.text, "html.parser")

        # 获取今天的中文星期
        weekday_map = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weekday = weekday_map[datetime.now().weekday()]
        result = {weekday: []}

        logging.info("正在查找今日更新模块...")

        today_updates_items = []

        # 方法 1: 查找明确标题为 "今日更新" 的 section
        update_sections = soup.find_all('section', class_='mod_figure_list')
        for section in update_sections:
            title_div = section.find('div', class_='mod_figure_list_title')
            if title_div and "每日更新" in title_div.get_text():
                logging.info("找到 '每日更新' 标题的 section。")
                today_updates_items = section.select('li.list_item')
                if today_updates_items:
                    break  # 找到 section，无需检查其他 section

        # 方法 2: 如果未找到 "每日更新" section，尝试通过 ID 查找时间表模块
        if not today_updates_items:
            logging.info("尝试通过 ID 查找时间表模块...")
            schedule_module = soup.find('div', id='schedule')
            if schedule_module:
                logging.info("找到时间表模块。")
                # 查找 '今天' 标签，然后查找其对应的内容
                today_tab = schedule_module.find('div', class_='tab_item', string='今天')
                if today_tab:
                    # 活跃标签的内容通常有 'tab_content_active' 或类似。
                    # 或者，有时它只是下一个兄弟元素或具有特定 ID/class 的 div。
                    # 此选择器假定活跃内容在 'tab_content' 中且是活跃的。
                    # 一个更健壮的解决方案可能涉及检查 'data-index' 或 'data-tab' 属性（如果它们明确链接）。
                    # 目前，我们尝试在模块内查找任何列表项。
                    today_updates_items = schedule_module.select('div.tab_content li.list_item')
                    if today_updates_items:
                        logging.info("在时间表模块中找到 '今天' 标签内容。")

        # 方法 3: 备用方案 - 收集所有列表项，然后尽可能根据更新信息进行筛选。
        # 这是在无法明确标记 "今日" section 时的最后手段。
        if not today_updates_items:
            logging.warning("未找到明确的 '每日更新' 或 '今天' section。尝试选择所有潜在的更新项。")
            # 此选择器范围较广，可能包含非今日更新项。
            # 后期处理需要更加小心。
            today_updates_items = soup.select('li.list_item')

        if not today_updates_items:
            logging.warning("未使用任何方法找到更新内容。")
            return result

        logging.info(f"找到 {len(today_updates_items)} 个潜在的更新项。")

        for item in today_updates_items:
            # 提取动漫标题
            title = "未知标题"
            # 优先选择 'figure_title a'，因为它通常是直接的链接/标题
            title_tag = item.select_one('a.figure_title, div.figure_title a, div.figure_title')
            if title_tag:
                title = clean_text(title_tag.get_text(strip=True))

            # 根据标题中的关键词进行非动漫内容的基本过滤
            # 这是一种启发式方法，可能需要根据观察到的数据进行调整。
            # 此外，检查标题是否过短或过于通用，这可能表示是广告或不相关的项目。
            """
            if not any(keyword in title for keyword in
                       ["动漫", "动画", "番剧", "剧场版", "影院版", "第季", "第部", "全集"]) \
                    and len(title) > 3:  # 假设动漫标题通常超过 3 个字符
                logging.debug(f"跳过可能是非动漫的内容: '{title}'")
                continue
            """
            # 提取详情链接
            link = ""
            link_tag = item.select_one('a.figure, a.figure_title')  # 'a.figure' 通常是主要的点击区域
            if link_tag and link_tag.get('href'):
                link = normalize_url(link_tag['href'])

            # 提取更新集数（例如："更新至30集"）
            episodes = "更新信息未知"
            # 寻找特定的 class 或模式以获取集数信息
            episode_tag = item.select_one('div.figure_desc, div.figure_info, span.figure_update')
            if episode_tag:
                episodes = clean_text(episode_tag.get_text(strip=True))

            # 提取封面图片 URL
            img_url = ""
            # 优先使用 data-src（如果可用），然后是 src
            img_tag = item.select_one('img.figure_pic, img.pic, img[src*="qq.com/v"], img[data-src*="qq.com/v"]')
            if img_tag:
                img_url = img_tag.get('data-src') or img_tag.get('src', '')
                img_url = normalize_url(img_url)

                # 忽略 base64 占位图
                if img_url.startswith('data:image'):
                    img_url = ""

            # 提取更新说明/标题，如果它与集数信息不同
            update_info = ""
            # 此选择器需要与 'episode_tag' 区分开（如果可能）
            # 有时 'figure_caption' 可能包含比集数更广泛的信息
            caption_tag = item.select_one('div.figure_caption')
            if caption_tag and caption_tag != episode_tag:  # 确保它与 episode_tag 不同
                update_info = clean_text(caption_tag.get_text(strip=True))

            # 添加到结果
            anime_info = {
                "platform": "tencent",
                "title": title,
                "update_count": episodes,
                "update_info": update_info if update_info else episodes,  # 如果 update_info 可用则使用，否则使用 episodes
                "image": img_url,
                "link": link,
                "text": f"{title} | {episodes}{' | ' + update_info if update_info and update_info != episodes else ''}"
            }

            result[weekday].append(anime_info)
            logging.info(f"已添加: '{title}'")

        return result

    except requests.exceptions.Timeout:
        logging.error("请求超时。将在 10 秒后重试...")
        time.sleep(10)
        return fetch_qq_cartoon_today()  # 重试一次
    except requests.exceptions.TooManyRedirects:
        logging.error("重定向过多。请检查 URL。")
        return {}
    except requests.exceptions.RequestException as e:
        logging.error(f"网络请求错误: {str(e)}")
        return {}
    except Exception as e:
        logging.exception(f"获取腾讯动漫更新信息时发生意外错误: {str(e)}")  # 记录 traceback
        return {}
    finally:
        random_delay()


def save_results(results, filename="tencent_cartoon.json"):
    """将结果保存到 JSON 文件。"""
    if not results:
        logging.info("没有可保存的结果。")
        return

    file_path = os.path.join(os.getcwd(), filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logging.info(f"结果已保存到 {file_path}")


def print_results(results):
    """将获取到的动漫更新结果打印到控制台。"""
    if not results:
        logging.info("没有找到任何更新信息可供打印。")
        return

    weekday = list(results.keys())[0]
    if not results[weekday]:
        logging.info(f"{weekday} 没有找到更新的动漫。")
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
            logging.warning("未能获取今日更新信息。")

        # 在测试之间添加较长延迟，除非是最后一次测试
        if i < num_tests:
            logging.info(f"\n等待 10 秒后进行下一次测试 (测试 #{i + 1})...")
            time.sleep(10)

    print("\n所有测试完成！")

