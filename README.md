# 追播 (AniTracker) - 你的个人追番助手 🎬

## 项目简介

~~追播(AniTracker)是一个强大的追剧工具，专门设计用于帮助用户轻松追踪每日更新的动漫和剧集。通过爬取各大视频平台的节目更新信息，让用户能够及时了解自己关注的内容更新状态，合理安排观看时间。~~
该项目已经使用Rust的tauri重新实现，新的项目地址为：[ani-todo-app](https://github.com/bruceblink/ani-todo-app), 欢迎前往体验和使用。此项目将不再维护，但仍可以用来学习研究Python爬虫、Github Actions以及Docker等技术的使用。

## 功能特点

- 🔄 定时更新：自动抓取各大视频平台的最新更新信息
- 📺 多平台支持：目前支持蜜柑计划、腾讯视频、哔哩哔哩、爱奇艺和优酷等 后续将支持更多视频平台
- 💾 数据本地存储：所有信息保存在本地JSON文件中，方便查询和管理

## 今日更新

## 系统要求

- Python 3.12+
- 请查看 `pyproject.toml` 获取所需依赖包

## 安装步骤

1. 克隆仓库到本地：
    ```bash
    git clone https://github.com/BruceBlink/AniTracker
    cd AniTracker
    ```

2. 安装依赖：
    ```bash
    pip install --no-cache-dir .
    ```
## 使用说明

- **运行主程序**：

    ```bash
    python -m anitracker
    ```

- **docker-compose运行**：

  安装以及启动

    ```bash
    docker-compose -f docker-compose.yml -p anitracker up -d
    ```

  停止及卸载

    ```bash
    docker-compose -f docker-compose.yml -p anitracker down
    ```
  
- **docker运行**

  如果你没有安装docker-compose，可以直接使用以下命令运行：

  ```bash
  docker run -d --name anitracker -v ${PWD}/data:/app/data -v ${PWD}/logs:/app/logs likanug515/anitracker:latest
  ```

## 数据存储

直接更新在readme中和存储在data/**_cartoon.json文件中

## 项目文件说明

```txt
AniTracker/
├── anitracker/                  主程序包，包含核心逻辑和功能实现
│   ├── __init__.py               package初始化文件
│   ├── __main__.py               项目主程序入口
│── pyproject.toml                项目的描述文件
├── Dockerfile                    用于构建项目Docker镜像的配置文件
├── Makefile                      自动化构建和管理任务的脚本
├── README.md                     项目说明文档
├── docker-compose.yml            Docker Compose编排文件，定义多容器服务
├── LICENSE                       项目许可证文件
├── common/                       存放通用工具和基础模块
│   ├── __init__.py               package初始化文件
│   ├── common.py                 通用函数或类
│   ├── contants.py               常量定义
│   ├── decorators.py             装饰器相关代码
│   └── logger_setup.py           日志配置相关代码
├── config/                       配置相关模块
│   ├── __init__.py               package初始化文件              
│   └── config.py                 项目配置文件
├── data/                         存储动漫相关数据的JSON文件
├── logs/                         日志文件存放目录
├── platforms/                    各平台相关的爬虫或数据处理模块
│   ├── __init__.py               package初始化文件
│   ├── bilibili.py               哔哩哔哩数据处理
│   ├── iqiyi.py                  爱奇艺数据处理
│   ├── mikanani.py               蜜柑计划数据处理
│   ├── tencent.py                腾讯视频数据处理
│   └── youku.py                  优酷视频数据处理
└── utils/                        工具函数模块
    ├── __init__.py               package初始化文件          
    └── utils.py                  通用工具函数
```

## 贡献指南

欢迎对项目做出贡献！如果你有任何建议或发现了bug，请：

1. Fork 本仓库
2. 创建新的分支
3. 提交你的修改
4. 发起 Pull Request

## 未来计划

- [x] 支持更多视频平台
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

- 提交 [Issue](https://github.com/bruceblink/AniTracker/issues)
- [发送邮件](mailto:likanug.g@qq.com)

## 致谢

感谢所有为本项目做出贡献的开发者和用户。

---

**注意**：本项目仅用于个人学习和研究使用，请勿用于任何商业用途。在使用过程中请遵守相关网站的使用条款和规定。
