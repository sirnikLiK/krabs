import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from sklearn.model_selection import train_test_split

# Параметры исходного изображения
orig_height = 350
orig_width = 1360
channels = 3

# Множитель для уменьшения изображения втрое (по оси H и W)
scale = 1 / 3
# Вычисляем размеры изображения после масштабирования
resized_height = int(orig_height * scale)
resized_width = int(orig_width * scale)

# Количество классов
num_classes = 5

# Создание модели классификатора
input_shape = (resized_height, resized_width, channels)
model = Sequential(name="Image_Classifier")
model.add(Conv2D(32, (3, 3), activation='relu', padding="same", input_shape=input_shape))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(64, (3, 3), activation='relu', padding="same"))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(128, (3, 3), activation='relu', padding="same"))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))  # выход: 5 классов

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

model.summary()

# Обучаем модель
epochs = 10
batch_size = 32

history = model.fit(X_train, y_train,
                    epochs=epochs,
                    batch_size=batch_size,
                    validation_data=(X_test, y_test))

# Сохранение модели
model.save("Class.h5")

# Например, генерируем изображение для класса 2.
single_img = generate_image_by_class(cls=2)
# Нормализуем изображение к диапазону [0, 1]
single_img = single_img / 255.0


"""
# Передача единичного изображения в модель и интерпретация вывода
single_img = cv2.resize(orig_image, (resized_width, resized_height), interpolation=cv2.INTER_LINEAR)
single_img = single_img / 255.0

# Добавляем измерение батча (получим форму (1, resized_height, resized_width, 3))
single_img_batch = np.expand_dims(single_img, axis=0)

# Получаем предсказание от модели (вероятности для каждого класса)
prediction = model.predict(single_img_batch)
print("Вероятности по классам:", prediction)

# Определяем класс с максимальной вероятностью
predicted_class = np.argmax(prediction, axis=1)[0]
print("Предсказанный класс:", predicted_class)
"""
