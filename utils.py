import re

from common import Result


def update_today_section_in_readme(data: dict[str, list]) -> None:
    """
    更新 README.md 中的 "今日更新" 部分的内容
    :param data:
    :return:
    """
    weekday = list(data.keys())[0]
    items = data[weekday]
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

    if start_idx is not None and end_idx is not None and start_idx <= end_idx:
        today_md = [f"### {weekday} 番剧更新\n"]
        for item in items:
            title = item["title"]
            link = item["detail_url"]
            count = item["update_count"]
            text = f'{item["update_time"]} 更新' + (f' 更新至 {str(count)}集' if count else '')
            if link:
                today_md.append(f"- [{title}]({link}) - {text}\n")
            else:
                today_md.append(f"- {title} - {text}\n")
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
    merged: dict[str, list[Result]] = {}
    seen_map: dict[str, set[Result]] = {}

    for d in dicts:
        for key, lst in d.items():
            merged.setdefault(key, [])
            seen_map.setdefault(key, set())

            for item in lst:
                if item not in seen_map[key]:
                    seen_map[key].add(item)
                    merged[key].append(item)

    return merged


def print_results(results: dict[str, list]):
    """将获取到的动漫更新结果打印到控制台。"""
    if not results:
        print("没有找到任何更新信息可供打印。")
        return

    weekday = list(results.keys())[0]
    if not results[weekday]:
        print(f"{weekday} 没有找到更新的动漫。")
        return

    print(f"\n{weekday} 更新动漫列表:")
    print("=" * 80)

    for i, anime in enumerate(results[weekday], 1):
        print(f"{i}. {anime['title']}")
        print(f"   更新集数: {anime['update_count']}")
        if anime['update_info'] and anime['update_info'] != anime['update_count']:  # 避免冗余
            print(f"   更新说明: {anime['update_info']}")
        if anime['image_url']:
            print(f"   封面图片: {anime['image_url']}")
        if anime['detail_url']:
            print(f"   详情链接: {anime['detail_url']}")
        print("-" * 80)

    print(f"\n统计: 共找到 {len(results[weekday])} 部今日更新的动漫")


from datetime import datetime

# 获取当前本地时间（你的环境默认就是 +08:00 新加坡时区）
now = datetime.now()

# 常见格式示例
iso_date = now.strftime("%Y-%m-%d")  # 2025-06-17
iso_date_ld = now.strftime("%Y/%m/%d")  # 2025-06-17
iso_datetime = now.strftime("%Y-%m-%d %H:%M:%S")  # 2025-06-17 10:23:45
chinese_date = now.strftime("%Y年%m月%d日")  # 2025年06月17日
compact = now.strftime("%y%m%d")  # 250617
weekday = now.strftime("%A")  # Tuesday


# print(iso_date, iso_datetime, chinese_date, compact, weekday, sep="\n")

def extract_number(text: str) -> int | None:
    """ 从字符串中提取第一个数字并返回整数。"""
    match = re.search(r'\d+', text)
    return int(match.group()) if match else None
