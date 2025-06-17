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
            link = item["link"]
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


def merge_data(dict1: dict[str, list], dict2: dict[str, list]) -> dict[str, list]:
    """
    合并两个数据字典
    """
    merged_dict = {}
    for key in set(dict1.keys()) | set(dict2.keys()):
        merged_dict[key] = dict1.get(key, []) + dict2.get(key, [])
    return merged_dict


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
