# 配置项
IMAGE_NAME = likanug/anitrack
IMAGE_TAG = 1.0.0
FULL_IMAGE = $(IMAGE_NAME):$(IMAGE_TAG)

# 构建镜像
build:
	docker build -t $(FULL_IMAGE) -f docker/Dockerfile docker

# 发布版本
release:
	@read -p "Enter version (e.g. v1.2.3): " v; \
	git tag $$v && git push origin $$v && echo "Pushed tag $$v"

# 登录 Docker Hub（你第一次使用需要运行）
login:
	docker login

# 推送镜像到远程仓库
push: build
	docker push $(FULL_IMAGE)

# 清理本地镜像
clean:
	docker rmi $(FULL_IMAGE)

# 启动服务（使用 docker-compose）
up:
	docker-compose up -d

# 停止服务
down:
	docker-compose down

help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

