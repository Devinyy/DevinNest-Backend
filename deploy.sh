#!/bin/bash

# 服务器信息
SERVER_IP="47.103.9.13"
SERVER_USER="root"
REMOTE_DIR="/opt/devinnest-backend"

# 排除的文件和目录
EXCLUDE_PARAMS=(
    --exclude=".git/"
    --exclude=".env"
    --exclude="venv/"
    --exclude="__pycache__/"
    --exclude=".DS_Store"
    --exclude="*.pyc"
    --exclude=".idea/"
    --exclude=".vscode/"
    --exclude="data/devinnest.db"
)

echo "============================================"
echo "开始部署 DevinNest Backend 到 $SERVER_IP"
echo "============================================"

# 0. 清理旧目录（一次性操作，可保留或删除）
echo "[0/3] 清理旧部署目录..."
ssh "$SERVER_USER@$SERVER_IP" "rm -rf /opt/devinnest-backend"

# 1. 同步文件
echo "[1/3] 同步文件到服务器..."
rsync -avz --progress "${EXCLUDE_PARAMS[@]}" ./ "$SERVER_USER@$SERVER_IP:$REMOTE_DIR"

if [ $? -ne 0 ]; then
    echo "❌ 文件同步失败，请检查网络连接或权限。"
    exit 1
fi

# 2. 在服务器上构建并重启 Docker 服务
echo "[2/3] 重启远程服务..."

# 创建 daemon.json 配置国内镜像源 (如果不存在)
ssh "$SERVER_USER@$SERVER_IP" "mkdir -p /etc/docker && cat > /etc/docker/daemon.json <<EOF
{
  \"registry-mirrors\": [
    \"https://docker.m.daocloud.io\",
    \"https://dockerproxy.com\",
    \"https://mirror.baidubce.com\",
    \"https://docker.nju.edu.cn\"
  ]
}
EOF
systemctl daemon-reload && systemctl restart docker
"

# 尝试多种 docker compose 命令格式
echo "开始构建镜像并启动服务..."
ssh "$SERVER_USER@$SERVER_IP" "cd $REMOTE_DIR && (
    if docker compose version >/dev/null 2>&1; then
        docker compose up -d --build
    elif docker-compose version >/dev/null 2>&1; then
        docker-compose up -d --build
    else
        echo '❌ 未找到 docker compose 或 docker-compose 命令'
        exit 1
    fi
)"

if [ $? -ne 0 ]; then
    echo "❌ 远程命令执行失败。"
    exit 1
fi

# 3. 清理未使用的镜像（可选）
echo "[3/3] 清理旧镜像..."
ssh "$SERVER_USER@$SERVER_IP" "docker image prune -f"

echo "============================================"
echo "✅ 部署完成！"
echo "============================================"
