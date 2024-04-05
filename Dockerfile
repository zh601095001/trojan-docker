# 使用基于 Debian 的 Python 镜像，Debian 是 Ubuntu 的上游，兼容性较好
FROM python:3-bullseye

# 安装编译依赖和cron
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
       build-essential \
       cmake \
       libboost-all-dev \
       libssl-dev \
       libmariadb-dev \
       git \
       cron \
    # 由于cryptography库在安装时需要编译，可能需要额外的依赖
    && apt-get install -y \
       libffi-dev \
       libssl-dev \
       python3-pip \
    && pip install cryptography \
    # 清理缓存，减小镜像体积
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 克隆 Trojan 源代码
RUN git clone https://github.com/trojan-gfw/trojan.git /trojan \
    && cd /trojan \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make \
    && make install \
    # 清理不再需要的文件，减小镜像大小
    && rm -rf /trojan

# 拷贝 Trojan 配置模板和 Python 配置脚本
COPY config.json /config/config.json
COPY configurator.py /configurator.py
COPY wrapper.sh /wrapper.sh

## 设置 cron 作业自动更新证书
#RUN echo "0 0 * * * python /configurator.py && /wrapper.sh" > /etc/cron.d/cert-updater \
#    && chmod 0644 /etc/cron.d/cert-updater \
#    && crontab /etc/cron.d/cert-updater
#
# 使 wrapper.sh 可执行
RUN chmod +x /wrapper.sh

# 暴露 Trojan 使用的端口
EXPOSE 443

# 使用 CMD 启动 cron 服务，并保持前台运行
CMD ["/bin/sh","-c","/wrapper.sh"]