from keras.api.models import Sequential
from keras.api.layers import LSTM, Dense, Dropout
from keras.api.callbacks import EarlyStopping
from a01_my_dataset import MyDataset

class MyModel():
    def __init__(self, input_shape):
        self.early_stopping = EarlyStopping(monitor="val_loss", patience=5)
        self.model = Sequential([
            LSTM(128, input_shape=input_shape, return_sequences=True),
            Dropout(0.3),
            LSTM(64, return_sequences=False),
            Dropout(0.2),
            Dense(32, activation="relu"),
            Dense(2)
        ])
        self.model.compile(loss="mse", optimizer="adam", metrics=["mae"])
        
    def train(self, X_train, y_train):
        self.model.fit(
            X_train, y_train,
            epochs=50,
            batch_size=64,
            validation_split=0.2,
            callbacks=[self.early_stopping],
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
    TEST_SPLIT = 0.2
    
    my_data_set = MyDataset(AG_PATH)
    X_train, y_train, X_test, y_test = my_data_set.pipline_data()
    
    my_model = MyModel(input_shape=(WINDOW_SIZE, 6))
    my_model.train(X_train, y_train)
    
    my_model.evaluate(X_test, y_test)