# 使用 Python 3.10 作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装必要的系统依赖
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 升级 pip
RUN pip install --upgrade pip

# 安装 Python 包
RUN pip install --no-cache-dir importlib-metadata

# 安装所有 vnpy 包
RUN pip install --no-cache-dir \
    vnpy_ctastrategy \
    vnpy_ctabacktester \
    vnpy_datamanager \
    vnpy_sqlite \
    vnpy_ctp

# 设置工作目录
WORKDIR /app/trading

# 创建 volume 以持久化数据
VOLUME ["/app/trading"]

# 设置默认命令
CMD ["python3"] 