import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout

# Параметры
SEQ_LENGTH = 200
NUM_CLASSES = 8

# Создаём модель классификатора с использованием одномерных свёрточных слоёв.
input_shape = (SEQ_LENGTH, 1)
model = Sequential(name="Conv1D_Classifier")
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
# Выходной слой: NUM_CLASSES нейронов, softmax активация для классификации
model.add(Dense(NUM_CLASSES, activation='softmax'))

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.summary()

# Параметры обучения
epochs = 10
batch_size = 10

# Обучение модели
history = model.fit(
    X_train, Y_train,
    epochs=epochs,
    batch_size=batch_size,
    validation_data=(X_test, Y_test))

# Сохранение модели
model.save("Class.h5")


"""Пример загрузки модели из файла и её применения"""

import tensorflow as tf
from tensorflow.keras.models import load_model

# Загружаем сохранённую модель из файла
model = load_model('Class.h5')

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

# определяем класс сценария разрушения
y_pred = model.predict(X_test)
predicted_classes = np.argmax(y_pred, axis=1)
# print("Предсказанный класс:", predicted_classes[0])