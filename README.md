# 追播 (AniTrack) - 你的个人追剧助手 🎬

## 项目简介

追播(AniTrack)是一个强大的追剧工具，专门设计用于帮助用户轻松追踪每日更新的动漫和剧集。通过爬取各大视频平台的节目更新信息，让用户能够及时了解自己关注的内容更新状态，合理安排观看时间。

## 功能特点

- 🔄 定时更新：自动抓取各大视频平台的最新更新信息
- 📺 多平台支持：目前支持蜜柑计划，腾讯视频，哔哩哔哩，爱奇艺等 后续将支持更多视频平台
- 💾 数据本地存储：所有信息保存在本地JSON文件中，方便查询和管理

## 今日更新

### 星期三 番剧更新
- [一念永恒 第3季](https://v.qq.com/x/cover/mzc002003lw1kp8.html) - 2025/06/18 更新 更新至 54集
- [遮天](https://v.qq.com/x/cover/mzc00200n53vkqc.html) - 2025/06/18 更新 更新至 114集
- [诛仙合集篇](https://v.qq.com/x/cover/mzc00200phqxwd6.html) - 2025/06/18 更新 更新至 6集
- [剑道第一仙](https://v.qq.com/x/cover/mzc00200bkls85f.html) - 2025/06/18 更新 更新至 140集
- [吞天记](https://v.qq.com/x/cover/mzc00200t39giu5.html) - 2025/06/18 更新 更新至 12集
- [神印王座](https://v.qq.com/x/cover/mzc002007j7p5hn.html) - 2025/06/18 更新 更新至 163集
- [诛仙 第3季](https://v.qq.com/x/cover/mzc00200z195unq.html) - 2025/06/18 更新 更新至 3集
- [大夏剑主 动态漫画](http://www.iqiyi.com/v_2f1ar1e82rk.html) - 2025/06/18 更新 更新至 186集
- [神宠进化 动态漫画 第2季](http://www.iqiyi.com/v_1zmppdpww5o.html) - 2025/06/18 更新 更新至 80集
- [魔法小公主绮莉 动态漫画](http://www.iqiyi.com/v_1gn3zf8qr4k.html) - 2025/06/18 更新 更新至 64集
- [修真聊天群 动态漫画](http://www.iqiyi.com/v_1khwur3ntm4.html) - 2025/06/18 更新 更新至 50集
- [特工王妃虐渣记 动态漫画](http://www.iqiyi.com/v_11u444o3k1o.html) - 2025/06/18 更新 更新至 64集
- [被迫成为隐藏职业 动态漫画](http://www.iqiyi.com/v_23jscm9fkgg.html) - 2025/06/18 更新 更新至 58集
- [都市古仙医](http://www.iqiyi.com/v_1la70ef6oaw.html) - 2025/06/18 更新 更新至 79集
- [穿越后我成了团宠 动态漫画](http://www.iqiyi.com/v_1kl1g82i2wo.html) - 2025/06/18 更新 更新至 42集
- [逆天仙命：捡个婴儿当大佬 动态漫画](http://www.iqiyi.com/v_2b9tawusim4.html) - 2025/06/18 更新 更新至 39集
- [邪神降世，我有一座大凶狱 动态漫画](http://www.iqiyi.com/v_dp0rbk9hd4.html) - 2025/06/18 更新 更新至 54集
- [一世独尊](http://www.iqiyi.com/v_16zxzexerfg.html) - 2025/06/18 更新 更新至 132集
- [开局签到至尊丹田 动态漫画](http://www.iqiyi.com/v_2amiwl7pa8s.html) - 2025/06/18 更新 更新至 182集
- [神探双骄 动态漫画](http://www.iqiyi.com/v_2aoz08v35fk.html) - 2025/06/18 更新 更新至 31集
- [诡异游戏：我靠亿万功德氪通关 动态漫画](http://www.iqiyi.com/v_1vjgd7croug.html) - 2025/06/18 更新 更新至 103集
- [斗罗大陆5重生唐三 动态漫画](http://www.iqiyi.com/v_20079ouizgs.html) - 2025/06/18 更新 更新至 23集
- [全民诡异：开局掌握零元购 动态漫画](http://www.iqiyi.com/v_1t3om8emqd8.html) - 2025/06/18 更新 更新至 46集

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
- `bilibili.py`: 哔哩哔哩数据爬取模块
- `iqiyi.py`: 爱奇艺数据爬取模块
- `youku.py`: 优酷数据爬取模块
- `common.py`: 公共函数模块，包含数据处理和格式化逻辑
- `decorators.py`: 装饰器模块，用于日志记录和异常处理
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
- [ ] 📅 每日更新提醒：及时获取最新剧集更新信息
- [ ] 🎯 个性化追踪：可以根据个人喜好设置关注的节目
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
