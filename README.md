## 基于rosbag的神经网络训练
### 安装python相关库
```
conda create -n rosbag python=3.10 -y
conda activate rosbag
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt
```
### 安装ROS的Docker版本
```
# 制作镜像
docker build -f .devcontainer/Dockerfile -t ros-tensorflow-gpu .

# 启动并进入镜像
docker run --gpus all --name ros-tensorflow-gpu -it ros-tensorflow-gpu /bin/bash

# 测试是否安装了cuda
python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
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

### VSCode接入docker开发环境
需安装Remote - Containers 插件
选择检视->命令选择区->Dev Containers Open Folder in Container

### 数据准备
数据以sqllite3的方式存储, 其中有imu数据和gps数据两种

### 数据预处理
+ imu数据生成频率为200hz, gps数据生成频率为20hz, 意味着imu生成了10条数据, gps才生成1条数据, 两者都含时间戳
+ 需要将gps数据和imu数据按时间戳对齐
+ 输入数据为imu数据, 标签为gps数据

### 基于神经网络的训练
由于是时间序列数据, 会采用lstm算法处理输入数据, 3个lstm层再加一个全连接层和一个输出层
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

### 训练日志
可以看到大概20轮即可降下来
```
Epoch 1/1000
I0000 00:00:1741847453.354774   13601 cuda_dnn.cc:529] Loaded cuDNN version 90300
908/908 ━━━━━━━━━━━━━━━━━━━━ 25s 25ms/step - loss: 0.7590 - mae: 0.8276 - val_loss: 0.3978 - val_mae: 0.7313
Epoch 2/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 24ms/step - loss: 0.3517 - mae: 0.6672 - val_loss: 0.2768 - val_mae: 0.5345
Epoch 3/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 24ms/step - loss: 0.1853 - mae: 0.4115 - val_loss: 0.0858 - val_mae: 0.2548
Epoch 4/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 24ms/step - loss: 0.0792 - mae: 0.2444 - val_loss: 0.0424 - val_mae: 0.1687
Epoch 5/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 24ms/step - loss: 0.0475 - mae: 0.1821 - val_loss: 0.0656 - val_mae: 0.1835
Epoch 6/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0435 - mae: 0.1634 - val_loss: 0.0684 - val_mae: 0.1599
Epoch 7/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 24ms/step - loss: 0.0456 - mae: 0.1563 - val_loss: 0.0201 - val_mae: 0.0868
Epoch 8/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 24ms/step - loss: 0.0370 - mae: 0.1355 - val_loss: 0.0161 - val_mae: 0.0760
Epoch 9/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 24ms/step - loss: 0.0293 - mae: 0.1172 - val_loss: 0.0166 - val_mae: 0.0777
Epoch 10/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 24ms/step - loss: 0.0174 - mae: 0.0945 - val_loss: 0.0117 - val_mae: 0.0605
Epoch 11/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0294 - mae: 0.1123 - val_loss: 0.0116 - val_mae: 0.0601
Epoch 12/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0148 - mae: 0.0833 - val_loss: 0.0097 - val_mae: 0.0516
Epoch 13/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0136 - mae: 0.0776 - val_loss: 0.0143 - val_mae: 0.0673
Epoch 14/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0137 - mae: 0.0801 - val_loss: 0.0084 - val_mae: 0.0497
Epoch 15/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0112 - mae: 0.0703 - val_loss: 0.0079 - val_mae: 0.0475
Epoch 16/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0097 - mae: 0.0664 - val_loss: 0.0080 - val_mae: 0.0457
Epoch 17/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0096 - mae: 0.0647 - val_loss: 0.0083 - val_mae: 0.0497
Epoch 18/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0117 - mae: 0.0702 - val_loss: 0.0073 - val_mae: 0.0478
Epoch 19/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0080 - mae: 0.0614 - val_loss: 0.0064 - val_mae: 0.0428
Epoch 20/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0081 - mae: 0.0601 - val_loss: 0.0055 - val_mae: 0.0387
Epoch 21/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0070 - mae: 0.0564 - val_loss: 0.0077 - val_mae: 0.0515
Epoch 22/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0072 - mae: 0.0589 - val_loss: 0.0049 - val_mae: 0.0371
Epoch 23/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0063 - mae: 0.0543 - val_loss: 0.0047 - val_mae: 0.0356
Epoch 24/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0057 - mae: 0.0520 - val_loss: 0.0041 - val_mae: 0.0331
Epoch 25/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0057 - mae: 0.0521 - val_loss: 0.0040 - val_mae: 0.0346
Epoch 26/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0052 - mae: 0.0506 - val_loss: 0.0040 - val_mae: 0.0348
Epoch 27/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0049 - mae: 0.0497 - val_loss: 0.0044 - val_mae: 0.0364
Epoch 28/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0053 - mae: 0.0507 - val_loss: 0.0036 - val_mae: 0.0332
Epoch 29/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0043 - mae: 0.0475 - val_loss: 0.0034 - val_mae: 0.0322
Epoch 30/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0041 - mae: 0.0464 - val_loss: 0.0040 - val_mae: 0.0354
Epoch 31/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0040 - mae: 0.0467 - val_loss: 0.0032 - val_mae: 0.0319
Epoch 32/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0037 - mae: 0.0451 - val_loss: 0.0040 - val_mae: 0.0332
Epoch 33/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0039 - mae: 0.0462 - val_loss: 0.0030 - val_mae: 0.0308
Epoch 34/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0037 - mae: 0.0447 - val_loss: 0.0028 - val_mae: 0.0296
Epoch 35/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0035 - mae: 0.0440 - val_loss: 0.0029 - val_mae: 0.0303
Epoch 36/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0033 - mae: 0.0434 - val_loss: 0.0027 - val_mae: 0.0300
Epoch 37/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0032 - mae: 0.0429 - val_loss: 0.0028 - val_mae: 0.0299
Epoch 38/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0032 - mae: 0.0429 - val_loss: 0.0025 - val_mae: 0.0290
Epoch 39/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0031 - mae: 0.0424 - val_loss: 0.0027 - val_mae: 0.0295
Epoch 40/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 23s 25ms/step - loss: 0.0031 - mae: 0.0427 - val_loss: 0.0025 - val_mae: 0.0291
Epoch 41/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0030 - mae: 0.0419 - val_loss: 0.0025 - val_mae: 0.0287
Epoch 42/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 22s 25ms/step - loss: 0.0029 - mae: 0.0417 - val_loss: 0.0024 - val_mae: 0.0281
Epoch 43/1000
908/908 ━━━━━━━━━━━━━━━━━━━━ 23s 25ms/step - loss: 0.0029 - mae: 0.0416 - val_loss: 0.0026 - val_mae: 0.0293
```