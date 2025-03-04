FROM ubuntu:focal-20241011

# 设置工作目录
WORKDIR /app

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive TZ=Asia/Taipei apt-get -y install tzdata

# 安装必要的系统依赖
RUN apt-get install -y \
    git \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    wget \
    locales \
    software-properties-common \
    curl \
    && rm -rf /var/lib/apt/lists/*

# install python3.10
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update && apt install -y python3.10 python3.10-venv python3.10-dev 
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

# 升级 pip
RUN python3.10 -m pip install --upgrade pip

# 安装 Python 包
RUN python3.10 -m pip install --no-cache-dir importlib-metadata
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
RUN python3.10 -m pip install --upgrade setuptools


RUN python3.10 -m pip install numpy==1.23.1
WORKDIR /root
RUN wget https://pip.vnpy.com/colletion/ta-lib-0.4.0-src.tar.gz
RUN tar -xf ta-lib-0.4.0-src.tar.gz
WORKDIR /root/ta-lib
RUN ./configure --prefix=/usr/local
RUN make -j1
RUN make install
RUN python3.10 -m pip install ta-lib==0.4.24

WORKDIR /root/
RUN git clone --branch 3.9.4 https://github.com/vnpy/vnpy.git
WORKDIR /root/vnpy
RUN python3.10 -m pip install -e .

# 安装所有 vnpy 包
RUN python3.10 -m pip install --no-cache-dir \
    vnpy_ctastrategy \
    vnpy_portfoliostrategy \
    vnpy_ctabacktester \
    vnpy_datamanager \
    vnpy_sqlite \
    vnpy_ctp

RUN python3.10 -m pip install yfinance

RUN mkdir /app/strategy_test
COPY . /app/strategy_test

# 设置工作目录
WORKDIR /app/strategy_test

# 创建 volume 以持久化数据
VOLUME ["/app/strategy_test"]

