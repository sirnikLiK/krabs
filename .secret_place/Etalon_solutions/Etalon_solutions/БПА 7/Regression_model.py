import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout

# Параметры генератора
SEQ_LENGTH = 200
BATCH_SIZE = 32

# Создаем модель для регрессии.
input_shape = (SEQ_LENGTH, 1)
model = Sequential(name="Conv1D_Regressor")
model.add(Conv1D(filters=32, kernel_size=3, activation='relu', padding='same', input_shape=input_shape))
model.add(MaxPooling1D(pool_size=2))
model.add(Dropout(0.3))

model.add(Conv1D(filters=64, kernel_size=3, activation='relu', padding='same'))
model.add(MaxPooling1D(pool_size=2))
model.add(Dropout(0.3))

model.add(Conv1D(filters=128, kernel_size=3, activation='relu', padding='same'))
model.add(MaxPooling1D(pool_size=2))
model.add(Dropout(0.3))

model.add(Flatten())
model.add(Dense(64, activation='relu'))
model.add(Dense(1, activation='linear'))  # выходной нейрон для регрессионного предсказания


model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
              loss='mse',
              metrics=['mae'])

model.summary()

# Параметры обучения
steps_per_epoch = 100  # батчей на эпоху
epochs = 10

# Обучение модели
history = model.fit(
    X_train, Y_train,
    epochs=epochs,
    batch_size=batch_size,
    validation_data=(X_test, Y_test))

# Сохранение модели
model.save("Regress_1.h5")


import tensorflow as tf
from tensorflow.keras.models import load_model

# Загружаем сохранённую модель из файла
model = load_model('Regress_1.h5')

# Генерируем показания акселерометра в том виде,
# в котором мы получаем их от сервера
strintg_chis = '0'
for i in range(1, 200):
  strintg_chis = strintg_chis + " " + str(i)
# print(strintg_chis)

# Готовим данные для поступления на вход нейронной сети
def string_to_numpy_array(data_string: str, dtype=float) -> np.ndarray:
    string_numbers = data_string.split()
    numeric_values = list(map(dtype, string_numbers))
    numpy_array = np.array(numeric_values)
    return numpy_array

X_test = string_to_numpy_array(strintg_chis)
X_test = np.expand_dims(X_test, axis=1)
X_test = np.expand_dims(X_test, axis=0)

# Предсказываем оставшийся срок службы для конкретного сценария
y_pred = model.predict(X_test)
y_pred = round(y_pred[0][0])
# print(y_pred)