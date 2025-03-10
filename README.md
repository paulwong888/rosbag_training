## 基于rosbag的神经网络训练
### 安装python相关库
```
conda create -n rosbag python=3.10 -y
conda activate rosbag
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt
```
### 安装ROS
```
sudo apt install ros-humble-geographic-msgs
# Replace ".bash" with your shell if you're not using bash
# Possible values are: setup.bash, setup.sh, setup.zsh
source /opt/ros/humble/setup.bash

cd /home/ws
colcon build
source install/setup.bash

cd /home/ws/src
ros2 pkg create my_python_pkg --build-type ament_python

ros2 interface show geographic_msgs/msg/GeoPoint

sudo apt install ros-humble-rosbag2 ros-humble-rosbag2-py
```