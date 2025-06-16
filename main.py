import json

from mikanani import fetch_mikanani_today


def main():
    data = fetch_mikanani_today()
    with open("mikanani_today.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()