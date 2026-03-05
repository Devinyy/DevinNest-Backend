# DevinNest Backend 部署指南

本指南将帮助您将 DevinNest Backend 部署到阿里云服务器（IP: 47.103.9.13）。

## 前置准备

1.  **本地代码准备**：
    确保您已提交所有更改到 Git 仓库，或者准备将本地代码直接复制到服务器。

2.  **服务器环境**：
    假设服务器运行的是 Ubuntu 或 CentOS。

## 步骤 1：连接服务器

使用 SSH 连接到您的服务器：
```bash
ssh root@47.103.9.13
# 输入密码
```

## 步骤 2：安装 Docker 和 Docker Compose

如果服务器尚未安装 Docker，请执行以下命令（以 Ubuntu 为例）：

```bash
# 更新软件包索引
sudo apt-get update

# 安装 Docker
sudo apt-get install -y docker.io

# 启动 Docker 并设置开机自启
sudo systemctl start docker
sudo systemctl enable docker

# 安装 Docker Compose
sudo apt-get install -y docker-compose
```

## 步骤 3：部署项目代码

您可以选择通过 Git 克隆或 SCP 上传代码。

**方式 A：Git 克隆（推荐）**
```bash
# 进入部署目录
cd /opt
# 克隆仓库（请替换为您的仓库地址）
git clone <your-git-repo-url> devinnest-backend
cd devinnest-backend
```

**方式 B：SCP 上传（本地执行）**
```bash
# 在本地项目根目录执行
scp -r . root@47.103.9.13:/opt/devinnest-backend
```

## 步骤 4：配置环境变量

在服务器项目目录下创建 `.env` 文件：
```bash
cd /opt/devinnest-backend
nano .env
```
粘贴您的环境变量配置（参考本地 .env）。

## 步骤 5：启动服务

使用 Docker Compose 启动服务：
```bash
# 构建并后台启动
docker-compose up -d --build
```
查看日志确保启动成功：
```bash
docker-compose logs -f
```

## 步骤 6：配置 Nginx 反向代理

为了让 `devinnest-api.top` 指向您的服务，我们需要配置 Nginx。

1.  **安装 Nginx**：
    ```bash
    sudo apt-get install -y nginx
    ```

2.  **配置站点**：
    创建一个新的配置文件：
    ```bash
    sudo nano /etc/nginx/sites-available/devinnest.conf
    ```
    粘贴以下内容（根据项目中的 `nginx.conf.template`）：
    ```nginx
    server {
        listen 80;
        server_name devinnest-api.top;

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

3.  **启用配置并重启 Nginx**：
    ```bash
    sudo ln -s /etc/nginx/sites-available/devinnest.conf /etc/nginx/sites-enabled/
    sudo nginx -t  # 检查配置语法
    sudo systemctl restart nginx
    ```

## 步骤 7：验证

在浏览器访问 `http://devinnest-api.top/docs`，应该能看到 Swagger 文档页面。

## 常见问题

1.  **端口未开放**：
    确保阿里云的安全组规则已开放 80 端口（HTTP）和 22 端口（SSH）。如果您使用 HTTPS，还需要开放 443 端口。

2.  **Cloudflare 设置**：
    在 Cloudflare DNS 设置中，确保 A 记录 `devinnest-api.top` 指向 `47.103.9.13`。
    如果在 Cloudflare 开启了 "Proxy status: Proxied"（橙色云朵），建议 SSL/TLS 设置为 "Flexible" 或 "Full"（取决于 Nginx 是否配置了 SSL 证书）。本指南目前配置的是 HTTP (80)，建议使用 Flexible。
