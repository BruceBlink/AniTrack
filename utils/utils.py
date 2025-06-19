import dataclasses
import json
import logging
import os
import random
import re
import tempfile
import time
from collections import defaultdict
from datetime import datetime

from common import Result

# 获取当前本地时间（你的环境默认就是 +08:00 新加坡时区）
now = datetime.now()

# 常见格式示例
iso_date = now.strftime("%Y-%m-%d")  # 2025-06-17
iso_date_ld = now.strftime("%Y/%m/%d")  # 2025/06/17
iso_datetime = now.strftime("%Y-%m-%d %H:%M:%S")  # 2025-06-17 10:23:45
chinese_date = now.strftime("%Y年%m月%d日")  # 2025年06月17日
compact = now.strftime("%y%m%d")  # 250617
weekday = now.strftime("%A")  # Tuesday
weekday_today = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][datetime.now().weekday()]


def update_today_section_in_readme(data: dict[str, list]) -> None:
    """
    更新 README.md 中的 "今日更新" 部分的内容
    :param data:
    :return:
    """
    _weekday = list(data.keys())[0]
    items = data[_weekday]
    with open("README.md", "r", encoding="utf-8") as f:
        lines = f.readlines()

    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "## 今日更新":
            start_idx = i + 2  # 跳过标题和空行
        if line.strip() == "## 系统要求":
            end_idx = i
            break

    if start_idx and end_idx and start_idx <= end_idx:
        today_md = [f"### {_weekday} 番剧更新\n"]
        for item in items:
            title = item["title"]
            link = item["detail_url"]
            count = item["update_count"]
            text = f'{item["update_time"]} 更新' + (
                f' 更新至{str(count)}集' if count else '') + f' 【{item["platform"]}】'
            if link:
                today_md.append(f"- [{title}]({link}) - {text}\n")
            else:
                today_md.append(f"- {title} - {text}\n")
        today_md.append(f"\n**今天总共更新了 {len(items)} 部番剧。**\n")
        # 保证末尾有空行
        today_md[-1] += "\n"
        lines[start_idx:end_idx] = today_md

        with open("README.md", "w", encoding="utf-8") as f:
            f.writelines(lines)


def merge_dict_data(*dicts: dict[str, list[Result]]) -> dict[str, list[Result]]:
    """
    合并任意数量的数据字典，并去除重复元素。
    相同键下的列表会按传入顺序拼接，且只保留第一次出现的元素。

    要求：列表元素必须为可哈希类型，如使用 @dataclass(frozen=True) 的对象或者实现了__hash__函数的对象。
    """
    merged: dict[str, list[Result]] = defaultdict(list)
    seen: dict[str, set[Result]] = defaultdict(set)

    for d in dicts:
        if d:
            for key, seq in d.items():
                seen_for_key = seen[key]
                merged_for_key = merged[key]
                for item in seq:
                    if item not in seen_for_key:
                        seen_for_key.add(item)
                        merged_for_key.append(item)
    return dict(merged)


def print_results(results: dict[str, list]):
    """将获取到的动漫更新结果打印到控制台。"""
    if not results:
        print("没有找到任何更新信息可供打印。")
        return

    _weekday = list(results.keys())[0]
    if not results[_weekday]:
        print(f"{_weekday} 没有找到更新的动漫。")
        return

    print(f"\n{_weekday} 更新动漫列表:")
    print("=" * 80)

    for i, anime in enumerate(results[_weekday], 1):
        print(f"{i}. {anime['title']}")
        print(f"   更新集数: {anime['update_count']}")
        if anime['update_info'] and anime['update_info'] != anime['update_count']:  # 避免冗余
            print(f"   更新说明: {anime['update_info']}")
        if anime['image_url']:
            print(f"   封面图片: {anime['image_url']}")
        if anime['detail_url']:
            print(f"   详情链接: {anime['detail_url']}")
        print("-" * 80)

    print(f"\n统计: 共找到 {len(results[_weekday])} 部今日更新的动漫")


# print(iso_date, iso_datetime, chinese_date, compact, weekday, sep="\n")

def extract_number(text: str) -> int | None:
    """ 从字符串中提取第一个数字并返回整数。"""
    match = re.search(r'\d+', text)
    return int(match.group()) if match else None


def random_delay(min_sec=1.2, max_sec=4.5):
    """引入随机延迟，模拟人类行为并避免被封锁。"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    logging.debug(f"延迟了 {delay:.2f} 秒。")


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


def decode_url(url: str) -> str:
    """
    解码 URL 中的百分号编码字符。
    :param url: 需要解码的 URL 字符串。
    :return: 解码后的字符串。
    """
    if not url:
        return ""

    # 使用 urllib.parse.unquote 解码
    from urllib.parse import unquote
    return unquote(url)


def encode_url(url: str) -> str:
    """
    编码 URL 中的特殊字符为百分号编码。
    :param url: 需要编码的 URL 字符串。
    :return: 编码后的字符串。
    """
    if not url:
        return ""

    # 使用 urllib.parse.quote 编码
    from urllib.parse import quote
    return quote(url, safe='/:?&=')  # 保留常见的 URL 特殊字符


"""
from urllib.parse import urlparse, parse_qs, unquote, quote
import json

# Provided URL url = "https://acs.youku.com/h5/mtop.youku.columbus.home.query/1.0/?jsv=2.6.1&appKey=24679788&t
=1750220768413&sign=3ed82de6e51bbc0e70bc53efbcf5dfa5&api=mtop.youku.columbus.home.query&v=1.0&dataType=json&type
=original&data=%7B%22ms_codes%22%3A%222019061000%22%2C%22params%22%3A%22%7B%5C%22debug%5C%22%3A0%2C%5C%22utdid%5C
%22%3A%5C%22PhHYIOJk3XkCAXW5q5sGEV%2BC%5C%22%2C%5C%22appPackageKey%5C%22%3A%5C%22com.youku.pcweb%5C%22%2C%5C%22ip%5C
%22%3A%5C%22117.185.171.155%5C%22%2C%5C%22reqSubNode%5C%22%3A0%2C%5C%22gray%5C%22%3A%5C%220%5C%22%2C%5C%22pageNo%5C
%22%3A1%2C%5C%22bizKey%5C%22%3A%5C%22kuflix_pc_home%5C%22%2C%5C%22showNodeList%5C%22%3A0%2C%5C%22nodeKey%5C%22%3A%5C
%22WEBCOMIC%5C%22%2C%5C%22appKey%5C%22%3A%5C%2224679788%5C%22%2C%5C%22bizContext%5C%22%3A%5C%22%7B%7D%5C%22%7D%22%2C
%22system_info%22%3A%22%7B%5C%22appPackageKey%5C%22%3A%5C%22com.youku.pcweb%5C%22%2C%5C%22device%5C%22%3A%5C%22pcweb
%5C%22%2C%5C%22os%5C%22%3A%5C%22pcweb%5C%22%2C%5C%22ver%5C%22%3A%5C%221.0.0.0%5C%22%2C%5C%22userAgent%5C%22%3A%5C
%22Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(
KHTML%2C%20like%20Gecko)%20Chrome%2F137.0.0.0%20Safari%2F537.36%5C%22%2C%5C%22guid%5C%22%3A%5C%221590141704165YXe%5C
%22%2C%5C%22young%5C%22%3A0%2C%5C%22brand%5C%22%3A%5C%22%5C%22%2C%5C%22network%5C%22%3A%5C%22%5C%22%2C%5C%22ouid%5C
%22%3A%5C%22%5C%22%2C%5C%22idfa%5C%22%3A%5C%22%5C%22%2C%5C%22scale%5C%22%3A%5C%22%5C%22%2C%5C%22operator%5C%22%3A%5C
%22%5C%22%2C%5C%22resolution%5C%22%3A%5C%22%5C%22%2C%5C%22pid%5C%22%3A%5C%22%5C%22%2C%5C%22childGender%5C%22%3A0%2C
%5C%22zx%5C%22%3A0%2C%5C%22appkey%5C%22%3A%5C%2224679788%5C%22%7D%22%7D"

# 解析 URL
parsed = urlparse(url)
qs = parse_qs(parsed.query)
data_param = qs.get("data", [""])[0]

# 解码 data 参数
decoded_data = unquote(data_param)

# 尝试解析 JSON
try:
    json_data = json.loads(decoded_data)
except json.JSONDecodeError:
    json_data = {"error": "Invalid JSON"}

# 编码回 data 参数
reencoded_data = quote(decoded_data, safe='')


if __name__ == '__main__':
    print("Decoded data:", json.dumps(json_data, ensure_ascii=False, indent=2))
    print("Re-encoded data:", reencoded_data)
    print("Original URL:", url)
    print("Parsed query string:", qs)
    print("Decoded data parameter:", decoded_data)
    print("Re-encoded data parameter:", reencoded_data)
"""


def write_to_file(filename: str, content: str) -> None:
    """
    将内容写入指定文件。
    :param filename: 文件名
    :param content: 要写入的内容
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


def _default_serializer(o):
    """通用 JSON 序列化器，支持 dataclass、to_dict、__dict__ 及回退到字符串。"""
    if dataclasses.is_dataclass(o):
        return dataclasses.asdict(o)
    if hasattr(o, 'to_dict') and callable(o.to_dict):
        return o.to_dict()
    if hasattr(o, '__dict__'):
        return o.__dict__
    return str(o)


def save_data_to_json(
        filename,
        data,
        *,
        default=None,
        ensure_ascii=False,
        indent=2,
        sort_keys=True
):
    """
    原子化写入 JSON 文件，支持自定义序列化及自动建目录。
    """
    serializer = default or _default_serializer
    # 确保目录存在
    dir_path = os.path.dirname(os.path.abspath(filename)) or '.'
    os.makedirs(dir_path, exist_ok=True)

    # 写入临时文件
    with tempfile.NamedTemporaryFile('w', dir=dir_path, delete=False, encoding='utf-8') as tmp:
        json.dump(data, tmp,
                  ensure_ascii=ensure_ascii,
                  indent=indent,
                  sort_keys=sort_keys,
                  default=serializer)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = tmp.name

    # 原子替换
    os.replace(tmp_path, filename)
    logging.info(f"JSON 数据已安全保存到 {filename}")

