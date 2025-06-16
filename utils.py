def update_today_section_in_readme(data):
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
            text = item.get("text") or items.get("update_count")
            if link:
                today_md.append(f"- [{title}]({link}) - {text}\n")
            else:
                today_md.append(f"- {title} - {text}\n")
        # 保证末尾有空行
        today_md[-1] += "\n"
        lines[start_idx:end_idx] = today_md

        with open("README.md", "w", encoding="utf-8") as f:
            f.writelines(lines)


def merge_data(dict1:dict[str,list], dict2:dict[str,list]) -> dict[str, list]:
    """
    合并两个数据字典，优先保留 data1 中的条目。
    """
    merged_dict = {}
    for key in set(dict1.keys()) | set(dict2.keys()):
        merged_dict[key] = dict1.get(key, []) + dict2.get(key, [])
    return merged_dict
