from datetime import datetime

HEADERS =  {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "dnt": "1",
    "priority": "u=0, i",
    "referer": "https://www.google.com/",
    "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 "
                  "Safari/537.36 Edg/125.0.0.0"
}

weekday = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][datetime.now().weekday()]

# Base URLs for various anime and cartoon sites
TENCENT_CARTOON_BASE_URL = "https://v.qq.com/channel/cartoon"
MIKANANI_BASE_URL = "https://mikanani.me"
# Bilibili 国创
BILIBILI_GUOCHUANG_API = "https://api.bilibili.com/pgc/web/timeline?types=4&before=6&after=6"
# Bilibili 番剧
BILIBILI_ANIME_API = "https://api.bilibili.com/pgc/web/timeline?types=1&before=6&after=6"
# Youku 动漫
YOUKU_COMICS_API = "https://www.youku.com/ku/webcomic"
# iQIYI 动漫
IQIYI_CARTOON_API = "https://mesh.if.iqiyi.com/portal/lw/v7/channel/cartoon"
