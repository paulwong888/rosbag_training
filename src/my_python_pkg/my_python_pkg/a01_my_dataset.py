import numpy as np
import pandas as pd
from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
from rclpy.serialization import deserialize_message
from geographic_msgs.msg import GeoPoseWithCovarianceStamped
from sensor_msgs.msg import Imu
from sklearn.preprocessing import StandardScaler
from scipy.interpolate import interp1d
from pyproj import Proj, Transformer

class MyDataset():
    def __init__(self, db3_file, break_size=500):
        self.break_size = break_size
        self.storage_options = StorageOptions(uri=db3_file, storage_id='sqlite3')
        self.converter_options = ConverterOptions()
        self.reader = SequentialReader()
        
    
    def extract_data_from_rosbag2(self):
        
        self.reader.open(self.storage_options, self.converter_options)

        imu_data = []
        gps_data = []
        index = 0
        
        # 初始化坐标系转换
        origin_set = False
        lat0, lon0, alt0 = 0, 0, 0
        utm_proj = None
        transformer = None

        while self.reader.has_next():
            index += 1
            print(index)
            topic, data, timestamp = self.reader.read_next()
            if topic == '/sensor/imu':
                msg: Imu = deserialize_message(data, Imu)
                imu_data.append(
                   [timestamp,
                    msg.linear_acceleration.x, 
                    msg.linear_acceleration.y, 
                    msg.linear_acceleration.z,
                    msg.angular_velocity.x, 
                    msg.angular_velocity.y, 
                    msg.angular_velocity.z]
                )
            elif topic == '/cx/gps/geo_pose':
                msg: GeoPoseWithCovarianceStamped = deserialize_message(data, GeoPoseWithCovarianceStamped)
                lat = msg.pose.pose.position.latitude
                lon = msg.pose.pose.position.longitude
                alt = msg.pose.pose.position.altitude
                
                # 初始化坐标系转换
                if not origin_set:
                    lat0, lon0, alt0 = lat, lon, alt
                    utm_proj = Proj(proj='utm', zone=int((lon0 + 180)/6 + 1), ellps='WGS84')
                    transformer = Transformer.from_proj(
                        Proj(proj='latlong', ellps='WGS84'),
                        utm_proj
                    )
                    origin_set = True
                
                # 转换为UTM坐标（北东地）
                x, y = transformer.transform(lon, lat)
                z = alt - alt0
                gps_data.append([timestamp, x, y])
                
            if index > self.break_size: 
                break

        return np.array(imu_data), np.array(gps_data)
    
    def pre_process_data(self, imu_data, gps_data, window_size=100):

        # 时间对齐（将GPS数据插值到IMU时间戳）
        imu_timestamps = imu_data[:, 0].astype(np.float64)
        gps_timestamps = gps_data[:, 0].astype(np.float64)
        gps_positions = gps_data[:, 1:3].astype(np.float64)
        
        # 线性插值GPS数据
        interp_x = np.interp(imu_timestamps, gps_timestamps, gps_positions[:, 0])
        interp_y = np.interp(imu_timestamps, gps_timestamps, gps_positions[:, 1])
        # interp_y = np.interp(imu_timestamps, gps_positions[:, 1])
        
        # 创建滑动窗口
        X, y = [], []
        for i in range(window_size, len(imu_data)):
            # 取窗口内的IMU数据（排除时间戳列）
            window = imu_data[i-window_size:i, 1:7]
            # 取当前时刻的插值GPS位置
            target = np.array([interp_x[i], interp_y[i]])
            X.append(window)
            y.append(target)
        
        return np.array(X), np.array(y)
    
    def train_test_split(self, X, y, test_spilt=0.2):
        
        # 数据标准化
        scaler_imu = StandardScaler()
        X = scaler_imu.fit_transform(X.reshape(-1, 6)).reshape(X.shape)
        
        scaler_gps = StandardScaler()
        y = scaler_gps.fit_transform(y)
        
        # 划分数据集
        split_idx = int(len(X) * (1 - test_spilt))
        X_train, y_train = X[:split_idx], y[:split_idx]
        X_test, y_test = X[split_idx:], y[split_idx:]
        
        return X_train, y_train, X_test, y_test
    
    def data_augmentation(self, X_train, y_train):
        # 添加高斯噪声
        noise_level = 0.02
        X_noisy = X_train + np.random.normal(0, noise_level, X_train.shape)
        
        # 时间序列反转
        X_flipped = X_train[:, ::-1, :]
        y_flipped = y_train
        
        # 振幅缩放
        scale_factors = np.random.uniform(0.9, 1.1, X_train.shape[0])
        X_scaled = X_train * scale_factors[:, np.newaxis, np.newaxis]
        
        return np.vstack([X_train, X_noisy, X_flipped, X_scaled]), \
            np.vstack([y_train, y_train, y_flipped, y_train])
    
    def pipline_data(self, window_size=100, test_spilt=0.2):
        imu_data, gps_data = self.extract_data_from_rosbag2()
        X, y = self.pre_process_data(imu_data, gps_data, window_size)
        X_train, y_train, X_test, y_test = self.train_test_split(X, y, test_spilt)
        X_train, y_train = self.data_augmentation(X_train, y_train)
        
        return X_train, y_train, X_test, y_test

if __name__ == "__main__":
    my_data_set = MyDataset('data/rosbag2_2025_03_05-16_06_21_0.db3')
    imu_data, gps_data = my_data_set.extract_data_from_rosbag2()
    print(imu_data)
    print(gps_data)
    
    X, y = my_data_set.pre_process_data(imu_data, gps_data)
    print(X)
    print(y)
    
    X_train, y_train, X_test, y_test = my_data_set.train_test_split(X, y)
    print(X_train)
    print(y_train)
    print(X_test)
    print(y_test)