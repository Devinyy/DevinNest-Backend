FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
# 使用阿里云 PyPI 镜像：服务器在阿里云内网，直连官方 PyPI 常因网络干扰返回空索引
# （表现为 "Could not find a version ... (from versions: none)"），改用镜像可稳定且更快
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
# --proxy-headers + --forwarded-allow-ips=* 让 uvicorn 信任 Nginx 转发的 X-Forwarded-Proto，
# 从而 request.base_url 能正确反映外部的 https 协议（容器唯一入口为本机 Nginx，故放行所有来源 IP）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
