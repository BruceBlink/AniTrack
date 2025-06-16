import json

from mikanani import fetch_mikanani_today
from utils import update_today_section_in_readme


def main():
    data = fetch_mikanani_today()
    print(json.dumps(data, ensure_ascii=False, indent=2))
    update_today_section_in_readme(data)
    # with open("mikanani_today.json", "w", encoding="utf-8") as f:
    #     json.dump(data, f, ensure_ascii=False, indent=2)
    # print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()