FROM osrf/ros:humble-desktop

ARG USERNAME=paul
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# 删除已存在的用户（例如 Ubuntu Noble 的默认用户）
RUN if id -u $USER_UID ; then userdel `id -un $USER_UID` ; fi

# 创建新用户并赋予 sudo 权限
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# 更新系统并安装基础依赖
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python3-pip

# 设置 pip 镜像源（需在安装依赖前执行）
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# ---------------------- 新增部分 ----------------------
# 安装 ROS 包
RUN apt-get install -y ros-humble-geographic-msgs

# 配置 ROS 环境（自动加载到用户的 .bashrc）
RUN echo "source /opt/ros/humble/setup.bash" >> /home/$USERNAME/.bashrc

# 确保 ROS 环境变量在容器启动时生效
ENV ROS_DISTRO=humble \
    ROS_VERSION=2
# ------------------------------------------------------

# 复制 requirements.txt 并安装 Python 依赖
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

# 确保 TensorFlow 能找到 GPU 运行时库
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# 设置环境变量
ENV SHELL=/bin/bash

# 复制应用代码
# COPY app /app
# WORKDIR /app

# 切换到非 root 用户
USER $USERNAME
CMD ["/bin/bash"]