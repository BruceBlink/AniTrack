# 追播 (AniTrack) - 你的个人追剧助手 🎬

## 项目简介

追播(AniTrack)是一个强大的追剧工具，专门设计用于帮助用户轻松追踪每日更新的动漫和剧集。通过爬取各大视频平台的节目更新信息，让用户能够及时了解自己关注的内容更新状态，合理安排观看时间。

## 功能特点

- 🔄 定时更新：自动抓取各大视频平台的最新更新信息
- 📺 多平台支持：目前支持蜜柑计划，后续将支持更多视频平台
- 📅 每日更新提醒：及时获取最新剧集更新信息
- 🎯 个性化追踪：可以根据个人喜好设置关注的节目
- 💾 数据本地存储：所有信息保存在本地JSON文件中，方便查询和管理

## 今日更新
### 星期一 番剧更新
- [转生成猫咪的大叔](https://mikanani.me/Home/Bangumi/3491) - 2025/06/16 更新 转生成猫咪的大叔
- [随兴旅-That's Journey-](https://mikanani.me/Home/Bangumi/3598) - 2025/06/16 更新 随兴旅-That's Journey-
- [夏日口袋](https://mikanani.me/Home/Bangumi/3599) - 2025/06/16 更新 夏日口袋
- [航海王](https://mikanani.me/Home/Bangumi/228) - 2025/06/16 更新 航海王
- [魔神创造传](https://mikanani.me/Home/Bangumi/3534) - 2025/06/16 更新 魔神创造传
- [魔女守护者](https://mikanani.me/Home/Bangumi/3587) - 2025/06/16 更新 魔女守护者
- [赛马娘 芦毛灰姑娘](https://mikanani.me/Home/Bangumi/3604) - 2025/06/16 更新 赛马娘 芦毛灰姑娘
- [受到猩猩之神庇护的大小姐在皇家骑士团受到宠爱](https://mikanani.me/Home/Bangumi/3608) - 2025/06/16 更新 受到猩猩之神庇护的大小姐在皇家骑士团受到宠爱
- [爱有些沉重的黑暗精灵从异世界追过来了](https://mikanani.me/Home/Bangumi/3617) - 2025/06/16 更新 爱有些沉重的黑暗精灵从异世界追过来了
- [快藏起来！玛琪娜同学!!](https://mikanani.me/Home/Bangumi/3621) - 2025/06/16 更新 快藏起来！玛琪娜同学!!
- [拉撒路](https://mikanani.me/Home/Bangumi/3624) - 2025/06/16 更新 拉撒路
- [时光流逝，饭菜依旧美味](https://mikanani.me/Home/Bangumi/3623) - 2025/06/16 更新 时光流逝，饭菜依旧美味
- [mono女孩](https://mikanani.me/Home/Bangumi/3628) - 2025/06/16 更新 mono女孩
- [药屋少女的呢喃 第二季](https://mikanani.me/Home/Bangumi/3530) - 2025/06/16 更新 药屋少女的呢喃 第二季
- [推理要在晚餐后](https://mikanani.me/Home/Bangumi/3605) - 2025/06/16 更新 推理要在晚餐后
- [摇滚乃是淑女的爱好](https://mikanani.me/Home/Bangumi/3606) - 2025/06/16 更新 摇滚乃是淑女的爱好
- [终末起点](https://mikanani.me/Home/Bangumi/3615) - 2025/06/16 更新 终末起点
## 系统要求

- Python 3.12+
- 请查看 `requirements.txt` 获取所需依赖包

## 安装步骤

1. 克隆仓库到本地：

```bash
git clone https://github.com/BruceBlink/WatchDaily
cd WatchDaily
```

1. 安装依赖：

```bash
pip install -r requirements.txt
```

## 使用说明

1. 运行主程序：

```bash
python main.py
```

1. 更新信息将保存在 `mikanani_today.json` 文件中

## 数据存储

- `mikanani_today.json`: 存储从蜜柑计划获取的每日更新信息

## 项目文件说明

- `mikanani.py`: 主程序文件，包含爬虫逻辑和数据处理
- `requirements.txt`: 项目依赖文件
- `mikanani_today.json`: 数据存储文件

## 贡献指南

欢迎对项目做出贡献！如果你有任何建议或发现了bug，请：

1. Fork 本仓库
2. 创建新的分支
3. 提交你的修改
4. 发起 Pull Request

## 未来计划

- [ ] 支持更多视频平台
- [ ] 添加图形用户界面（GUI）
- [ ] 添加订阅提醒功能
- [ ] 支持自定义过滤器
- [ ] 添加导出功能

## 许可证

本项目采用 MIT 许可证 - 详情请查看 [LICENSE](LICENSE) 文件

## 联系方式

如有任何问题或建议，欢迎通过以下方式联系：

- 提交 Issue
- 发送邮件至 [你的邮箱]

## 致谢

感谢所有为本项目做出贡献的开发者和用户。

---

**注意**：本项目仅用于个人学习和研究使用，请勿用于任何商业用途。在使用过程中请遵守相关网站的使用条款和规定。
