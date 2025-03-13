import tensorflow as tf
from keras.api.models import Sequential
from keras import regularizers
from keras.api.layers import LSTM, Dense, Dropout
from keras.api.callbacks import EarlyStopping
from keras.api.optimizers import Adam
from keras.api.optimizers.schedules import ExponentialDecay
from keras.api.losses import Huber
from a01_my_dataset import MyDataset

class MyModel():
    def __init__(self, input_shape):
        self.config_gpu()
        self.early_stopping = EarlyStopping(monitor="val_loss", patience=5)
        
        self.model = Sequential([
            LSTM(256, input_shape=input_shape, return_sequences=True,
                kernel_regularizer=regularizers.l2(0.001)),
            Dropout(0.4),
            LSTM(128, return_sequences=True,
                recurrent_regularizer=regularizers.l1_l2(0.001, 0.001)),
            Dropout(0.3),
            LSTM(64, return_sequences=False),
            Dropout(0.2),
            Dense(64, activation='swish',
                kernel_initializer='he_normal'),
            Dense(32, activation='swish'),
            Dense(2)
        ])
        
        # 自适应学习率配置
        optimizer = Adam(
            learning_rate=ExponentialDecay(
                initial_learning_rate=0.001,
                decay_steps=1000,
                decay_rate=0.9))
        
        self.model.compile(
            loss=Huber(),  # 对异常值更鲁棒
            optimizer=optimizer,
            metrics=['mae']
        )
        
    def config_gpu(self):
        gpus = tf.config.experimental.list_physical_devices("GPU")
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                print(f"已启用 {len(gpus)} 块GPU")
            except RuntimeError as e:
                print(e)
        
    def train(self, X_train, y_train):
        self.model.fit(
            X_train, y_train,
            epochs=1000,
            batch_size=256,
            validation_split=0.2,
            # callbacks=[self.early_stopping],
            verbose=1
        )
        
    def evaluate(self, X_test, y_test):
        test_loss = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"Test Loss: {test_loss[0]:.4f}, MAE: {test_loss[1]:.4f}")
        
    def save(self, save_model_path):
        self.model.save(save_model_path)
        
if __name__ == "__main__":
    AG_PATH = 'data/rosbag2_2025_03_05-16_06_21_0.db3'
    WINDOW_SIZE = 100  # 使用1秒的IMU数据（200Hz * 0.5s = 100 samples）
    BREAK_SIZE = 100000
    TEST_SPLIT = 0.2
    
    my_data_set = MyDataset(AG_PATH, BREAK_SIZE)
    X_train, y_train, X_test, y_test = my_data_set.pipline_data(WINDOW_SIZE, TEST_SPLIT)
    
    my_model = MyModel(input_shape=(WINDOW_SIZE, 6))
    my_model.train(X_train, y_train)
    
    my_model.evaluate(X_test, y_test)