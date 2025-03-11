## 基于rosbag的神经网络训练
### 安装python相关库
```
conda create -n rosbag python=3.10 -y
conda activate rosbag
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt
```
### 安装ROS和geographic-message
由于ROS针对ubuntu支持得比较好, 推荐基于docker的方式安装, [安装指南](https://docs.ros.org/en/jazzy/How-To-Guides/Setup-ROS-2-with-VSCode-and-Docker-Container.html)
安装geographic-message
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

### 数据准备
数据以sqllite3的方式存储, 其中有imu数据和gps数据两种

### 数据预处理
+ imu数据生成频率为200hz, gps数据生成频率为20hz, 意味着imu生成了10条数据, gps才生成1条数据, 两者都含时间戳
+ 需要将gps数据和imu数据按时间戳对齐
+ 输入数据为imu数据, 标签为gps数据

### 基于神经网络的训练
由于是时间序列数据, 会采用lstm算法处理输入数据, 再加一个全连接层和一个输出层
为简化编码, 使用keras框架编码

### 训练与评估
```
AG_PATH = 'data/rosbag2_2025_03_05-16_06_21_0.db3'
WINDOW_SIZE = 100  # 使用1秒的IMU数据（200Hz * 0.5s = 100 samples）
TEST_SPLIT = 0.2

my_data_set = MyDataset(AG_PATH)
X_train, y_train, X_test, y_test = my_data_set.pipline_data(WINDOW_SIZE, TEST_SPLIT)

my_model = MyModel(input_shape=(WINDOW_SIZE, 6))
my_model.train(X_train, y_train)

my_model.evaluate(X_test, y_test)
```