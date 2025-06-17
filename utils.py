from collections.abc import Mapping
from typing import Any, Dict, List


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
            text = item.get("text") or item.get("update_count") or "未知"
            if link:
                today_md.append(f"- [{title}]({link}) - {text}\n")
            else:
                today_md.append(f"- {title} - {text}\n")
        # 保证末尾有空行
        today_md[-1] += "\n"
        lines[start_idx:end_idx] = today_md

        with open("README.md", "w", encoding="utf-8") as f:
            f.writelines(lines)


def _freeze(obj: Any) -> Any:
    """
    将任意嵌套的 dict/list/set 转换为可哈希的签名：
      - dict -> frozenset of (key, freeze(value))
      - list -> tuple of freeze(item)
      - set -> frozenset of freeze(item)
      - 其他 -> 原样返回（假设本身是可哈希的）
    """
    if isinstance(obj, Mapping):
        return frozenset((k, _freeze(v)) for k, v in sorted(obj.items()))
    if isinstance(obj, list):
        return tuple(_freeze(v) for v in obj)
    if isinstance(obj, set):
        return frozenset(_freeze(v) for v in obj)
    return obj


def merge_dict_data(*dicts: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
    """
    合并任意数量的数据字典，并去除重复元素（支持元素为 dict/list等不可哈希类型）。
    相同键下的列表会按传入顺序拼接，且只保留第一次出现的元素。
    """
    merged: Dict[str, List[Any]] = {}
    seen_map: Dict[str, set] = {}

    for d in dicts:
        for key, lst in d.items():
            merged.setdefault(key, [])
            seen_map.setdefault(key, set())

            for item in lst:
                sig = _freeze(item)
                if sig not in seen_map[key]:
                    seen_map[key].add(sig)
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

print(iso_date, iso_datetime, chinese_date, compact, weekday, sep="\n")
