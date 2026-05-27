#!/bin/bash
set -euo pipefail

# 从线上服务器拉取「数据库一致性快照 + static 文件夹」到本地。
# 适用于低频手动备份：本地执行 ./backup.sh 即可，无需 OSS。

# 服务器信息（与 deploy.sh 保持一致）
SERVER_USER="root"
SERVER_IP="47.103.9.13"
REMOTE_DIR="/opt/devinnest-backend"
CONTAINER="devinnest-backend"   # docker-compose.yml 中的 container_name

# 本地备份目录
TS="$(date +%Y%m%d_%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKUP_DIR="$SCRIPT_DIR/backups"
DB_DIR="$BACKUP_DIR/db"
STATIC_DIR="$BACKUP_DIR/static"
mkdir -p "$DB_DIR" "$STATIC_DIR"

echo "============================================"
echo "从 $SERVER_IP 拉取线上数据 ($TS)"
echo "============================================"

# 1. 在服务器容器内生成数据库一致性快照（SQLite 在线备份，安全处理 WAL）
echo "[1/3] 生成数据库一致性快照..."
ssh "$SERVER_USER@$SERVER_IP" "docker exec $CONTAINER python -c \"import sqlite3; s=sqlite3.connect('/app/data/devinnest.db'); d=sqlite3.connect('/app/data/_snapshot.db'); s.backup(d); d.close(); s.close()\""

# 2. 拉取快照到本地（带时间戳保留历史），随后删除服务器上的临时快照
echo "[2/3] 拉取数据库快照 -> $DB_DIR/devinnest_$TS.db"
rsync -avz "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/data/_snapshot.db" "$DB_DIR/devinnest_$TS.db"
ssh "$SERVER_USER@$SERVER_IP" "rm -f $REMOTE_DIR/data/_snapshot.db"

# 3. 同步 static 文件夹（镜像最新状态；不加 --delete 以免误删本地已备份内容）
echo "[3/3] 同步 static 文件夹 -> $STATIC_DIR/"
rsync -avz "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/static/" "$STATIC_DIR/"

echo "============================================"
echo "✅ 备份完成"
echo "   数据库: $DB_DIR/devinnest_$TS.db"
echo "   static: $STATIC_DIR/"
echo "============================================"
