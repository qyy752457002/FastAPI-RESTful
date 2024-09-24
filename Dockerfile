# 使用 Python 3.12 作为基础镜像
FROM python:3.12

# 设置 容器工作目录 为 /app
WORKDIR /app

# 复制 requirements.txt 文件到 容器工作目录 /app
COPY requirements.txt .

# 在容器内运行 pip 命令来安装依赖项
# --no-cache-dir 标志用于防止 pip 缓存安装包，减少镜像体积
# --upgrade 标志用于升级已安装的软件包
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 复制当前目录下 (.) 所有文件到 容器工作目录 /app 下
COPY . .

# CMD: 在容器启动时，使用 Bash shell 执行 docker-entrypoint.sh 脚本
# Bash shell: 这是 Bash shell 的路径，用于在 Linux 系统中执行脚本和命令
# 它告诉 Docker 使用 Bash shell 来运行接下来的脚本
# docker-entrypoint.sh: 这是要执行的脚本或命令的名称
CMD ["/bin/bash", "docker-entrypoint.sh"]