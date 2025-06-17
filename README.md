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

### 星期二 番剧更新
- [转生成猫咪的大叔](https://mikanani.me/Home/Bangumi/3491) - 2025/06/17 更新
- [#COMPASS2.0 战斗天赋解析系统](https://mikanani.me/Home/Bangumi/3590) - 2025/06/17 更新
- [随兴旅-That's Journey-](https://mikanani.me/Home/Bangumi/3598) - 2025/06/17 更新
- [夏日口袋](https://mikanani.me/Home/Bangumi/3599) - 2025/06/17 更新
- [中禅寺老师的灵怪讲义实录 老师会把谜题全都解开的。](https://mikanani.me/Home/Bangumi/3601) - 2025/06/17 更新
- [正义使者 -我的英雄学院之非法英雄-](https://mikanani.me/Home/Bangumi/3619) - 2025/06/17 更新
- [魔女守护者](https://mikanani.me/Home/Bangumi/3587) - 2025/06/17 更新
- [受到猩猩之神庇护的大小姐在皇家骑士团受到宠爱](https://mikanani.me/Home/Bangumi/3608) - 2025/06/17 更新
- [拉撒路](https://mikanani.me/Home/Bangumi/3624) - 2025/06/17 更新
- [干杂活我乃最强～关于原英雄队伍的杂役人员，实际上除了战斗能力外全是SSS的故事～](https://mikanani.me/Home/Bangumi/3632) - 2025/06/17 更新
- [安妮·雪莉](https://mikanani.me/Home/Bangumi/3582) - 2025/06/17 更新
- [打了300年的史莱姆，不知不觉就练到了满级 ～其二～](https://mikanani.me/Home/Bangumi/3586) - 2025/06/17 更新
- [我是星际国家的恶德领主！](https://mikanani.me/Home/Bangumi/3592) - 2025/06/17 更新
- [时光流逝，饭菜依旧美味](https://mikanani.me/Home/Bangumi/3623) - 2025/06/17 更新
- [真･武士传 剑勇传说](https://mikanani.me/Home/Bangumi/3637) - 2025/06/17 更新
- [外星人姆姆](https://mikanani.me/Home/Bangumi/3594) - 2025/06/17 更新
- [拜托请穿上，鹰峰同学](https://mikanani.me/Home/Bangumi/3603) - 2025/06/17 更新
- [吞噬星空](https://v.qq.com/x/cover/324olz7ilvo2j5f.html) - 2025/06/17 更新 更新至 176集
- [万界独尊](https://v.qq.com/x/cover/mzc00200cu8uq8c.html) - 2025/06/17 更新 更新至 339集
- [星辰变 第6季](https://v.qq.com/x/cover/mzc002006wuirfi.html) - 2025/06/17 更新 更新至 16集
- [武神主宰](https://v.qq.com/x/cover/7q544xyrava3vxf.html) - 2025/06/17 更新 更新至 556集
- [炼气十万年](https://v.qq.com/x/cover/mzc002006n62s11.html) - 2025/06/17 更新 更新至 250集
- [诛仙合集篇](https://v.qq.com/x/cover/mzc00200phqxwd6.html) - 2025/06/17 更新 更新至 6集
- [灵剑尊](https://v.qq.com/x/cover/2w2legt0g8z26al.html) - 2025/06/17 更新 更新至 605集
- [一念永恒 第3季](https://v.qq.com/x/cover/mzc002003lw1kp8.html) - 2025/06/17 更新 更新至 54集
- [遮天](https://v.qq.com/x/cover/mzc00200n53vkqc.html) - 2025/06/17 更新 更新至 114集
- [我的师兄太强了](https://www.bilibili.com/bangumi/play/ep1524724) - 2025/06/17 更新 更新至 28集
- [大侠请上功](https://www.bilibili.com/bangumi/play/ep1508581) - 2025/06/17 更新 更新至 7集

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

## 数据存储
直接更新在readme中

## 项目文件说明

- `main.py`: 主程序文件，包含数据整合和更新到readme的逻辑  
- `mikanani.py`: 蜜柑计划数据爬取模块
- `tencent.py`: 腾讯视频数据爬取模块
- `utils.py`: 工具函数模块
- `config.py`: 配置文件，包含常量和配置参数
- `README.md`: 项目说明文件
- `requirements.txt`: Python依赖包列表
- `.github/workflows/`: GitHub Actions工作流配置
  - `mian.yml`: 自动更新README的工作流
- `.gitignore`: Git忽略文件列表
- `LICENSE`: 许可证文件

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
