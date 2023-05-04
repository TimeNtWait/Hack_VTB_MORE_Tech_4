"""Скрипт по обучению модели"""
import numpy as np
import pandas as pd

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, SpatialDropout1D, BatchNormalization, Embedding, Flatten, Activation
from tensorflow.keras.preprocessing.text import Tokenizer

from sklearn.model_selection import train_test_split
import pickle
import json

# Для конфигурации используется json
with open('config.json', 'r') as f:
    config = json.load(f)

MAX_COUNT_WORDS = 30000

union_train_data = pd.read_csv(config['DATASET_PATH'] + "union_train_data.csv", sep=";", skiprows=[0],
                               names=["link", "title", "description", "summary", "tags", "published_date",
                                      "description_preproc", "target", ])

x_data = union_train_data["description_preproc"]
y_data = union_train_data["target"]
y_data = np.array([[0., 1.] if t == "booker" else [1., 0.] for t in y_data])

# Разделяем обучающую и валидационную выборку
x_train, x_val, y_train, y_val = train_test_split(x_data, y_data, test_size=0.1, shuffle=True)

# Оубчаем токинизатор на основе обучающей выборки без валидационной, чтобы небыло утечки информации в модель
tokenizer = Tokenizer(num_words=MAX_COUNT_WORDS, filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n', lower=True, split=' ',
                      oov_token='unknown_token', char_level=False)
# формируем словарь частотности
tokenizer.fit_on_texts(x_train)
text_all_news = tokenizer.texts_to_matrix(x_train)

# Формируем последовтельность токенов для обучающей и валидационной выборки
train_bow_sequences = tokenizer.texts_to_sequences(x_train)
test_bow_sequences = tokenizer.texts_to_sequences(x_val)


# Формирование выборок по листу индексов слов
# Т.к. тексты разного размера их надо привести к одному виду,
# это будет сдлано за счет разбиения текстов на самостоятельные подстроки
# которые будут подаваться на обучение как полностью самостоятельные данные
# со своим таргетом. Под текстами имеется ввиду массив индексов слов

# функция дробления текста на подстроки опредленной длины
# функция принимает последовательность индексов, размер окна, шаг окна
def splt_word_sequences(words_indexes, len_str, step):
    sample_list = []  #
    index = 0  # Задаем начальный индекс
    while (index + len_str <= len(words_indexes)):  # Идём по всей длине вектора индексов
        sample_list.append(words_indexes[index:index + len_str])  # "Откусываем" векторы длины len_str
        index += step  # Смещаеммся вперёд на step
    return sample_list


# Формирование обучающей и проверочной выборки
# Из двух листов индексов от двух классов
# Функция принимает последовательность индексов, размер окна, шаг окна
def create_samples(wordIndexes, Y, xLen, step):
    # Создание обучающую/проверочную выборку из индексов
    classesXSamples = []  # Новые сэмлы данных
    for wI in wordIndexes:  # Для каждого текста выборки из последовательности индексов
        # Добавляем в список очередной текст индексов, разбитый на "кол-во окон*длину окна"
        classesXSamples.append(splt_word_sequences(wI, xLen, step))
        # Формируем один общий xSamples
    xSamples = []  # Здесь будет список размером "суммарное кол-во окон во всех текстах*длину окна (например, 15779*1000)"
    ySamples = []  # Здесь будет список размером "суммарное кол-во окон во всех текстах*вектор длиной 6"

    for t in range(len(wordIndexes)):  # В диапазоне кол-ва классов(6)
        xT = classesXSamples[t]  # Берем очередной текст вида "кол-во окон в тексте*длину окна"(например, 1341*1000)
        for i in range(len(xT)):  # И каждое его окно
            xSamples.append(xT[i])  # Добавляем в общий список выборки
            ySamples.append(Y[t])  # Добавляем соответствующий вектор класса
    xSamples = np.array(xSamples)  # Переводим в массив numpy для подачи в нейронку
    ySamples = np.array(ySamples)  # Переводим в массив numpy для подачи в нейронку

    return (xSamples, ySamples)  # Функция возвращает выборку и соответствующие векторы классов


#Задаём базовые параметры
xLen = 40 #Длина отрезка текста, по которой анализируем, в словах
step = 30 #Шаг разбиения исходного текста на обучающие векторы

#Формируем обучающую и тестовую выборку
xTrain, yTrain = create_samples(train_bow_sequences, y_train, xLen, step) #извлекаем обучающую выборку
xTest, yTest = create_samples(test_bow_sequences, y_val, xLen, step)    #извлекаем тестовую выборку

# Преобразовываем полученные выборки из последовательности индексов в матрицы нулей и единиц по принципу Bag of Words
xTrain01 = tokenizer.sequences_to_matrix(xTrain.tolist()) #Подаем xTrain в виде списка, чтобы метод успешно сработал
xTest01 = tokenizer.sequences_to_matrix(xTest.tolist()) # Подаем xTest в виде списка, чтобы метод успешно сработал



#Создаём полносвязную сеть
model = Sequential()
model.add(Dense(200, input_dim=30000, activation="relu"))
model.add(Dropout(0.25))
model.add(BatchNormalization())
model.add(Dense(2, activation='softmax'))
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

#Обучаем сеть на выборке, сформированной по bag of words - xTrain01
history = model.fit(xTrain01,
                      yTrain,
                      epochs=10,
                      batch_size=128,
                      validation_data=(xTest01, yTest))
print(history.history['accuracy'])
print(history.history['val_accuracy'])

# Сохранеие модели и токенизатора
# Сохранеие модели
model.save(config['MODEL_FILENAME'], save_format='h5')
# Сохранеие токенизатора
with open(config['TOKENIZER_FILENAME'], 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

# # loading
# with open('tokenizer.pickle', 'rb') as handle:
#     tokenizer = pickle.load(handle)

#
# import pickle
#
# # saving
# with open('tokenizer.pickle', 'wb') as handle:
#     pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
#
# # loading
# with open('tokenizer.pickle', 'rb') as handle:
#     tokenizer = pickle.load(handle)