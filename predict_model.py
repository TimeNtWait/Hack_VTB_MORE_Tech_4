"""Скрипт по обучению модели"""
import numpy as np
import pandas as pd

import tensorflow
import pickle
import json

# Для конфигурации используется json
with open('config.json', 'r') as f:
    config = json.load(f)

# MAX_COUNT_WORDS = 30000
MAX_COUNT_WORDS = config['MAX_COUNT_WORDS']


class PredictNews():
    def __init__(self):
        self.model = self.load_model(config['MODEL_FILENAME'])
        self.tokenizer = self.load_tokenizer(config['TOKENIZER_FILENAME'])

    def predict_from_df(self, df, columns):
        predicts = []
        count_similar_words = []
        rows = df[columns].values
        for row in rows:
            predicts.append(self.calc_predict(row[0]))
            count_similar_words.append(self.calc_similar_words(row[0]))
        df["predict"] = np.array(predicts)
        df["count_similar_words"] = np.array(count_similar_words)
        df = df.drop_duplicates(subset=['title', "summary"])
        return df[['title', 'summary', 'description', 'tags', 'link', 'published_dt', 'predict',
                   "count_similar_words"]].sort_values(by=['predict', 'count_similar_words'], ascending=False)

    def calc_predict(self, text):
        predict = self.predict(text)
        predict = self.calc_mean_predict(predict)
        return predict

    # TODO сделать получение наименоние для какой роли вызвается
    #  поиск новостей role, эта информция уже есть в df
    def calc_similar_words(self, text):
        role_keywords = config['ROLES_FEEDS']["booker"]["info"]
        role_keywords = [x.lower() for x in role_keywords]
        return sum([text.count(x) for x in role_keywords])

    def calc_mean_predict(self, predict):
        return np.mean(predict, axis=0)[1]

    def predict(self, text):
        test_tocken = self.tokenizer.texts_to_sequences([text])
        # Для случаев когда новость меньше чем нужный размер увеличиваем новость за счет себя сомой
        while len(test_tocken[0]) <= config['SIZE_WINDOW']:
            test_tocken[0] += test_tocken[0]
        x_test_parts, _ = self.createTestMultiClasses(test_tocken, config['SIZE_WINDOW'], config['STEP_WINDOW'])
        if x_test_parts.shape[1] <= 2:
            predict = self.model.predict(x_test_parts[0])
        else:
            predict = self.model.predict(x_test_parts[0][:-1])
        return predict

    def load_model(self, filename):
        model = tensorflow.keras.models.load_model(filename)
        return model

    def load_tokenizer(self, filename):
        with open(filename, 'rb') as handle:
            tokenizer = pickle.load(handle)
        return tokenizer

    # функция дробления текста на подстроки опредленной длины
    # функция принимает последовательность индексов, размер окна, шаг окна
    def __splt_word_sequences(self, words_indexes, len_str, step):
        sample_list = []  #
        index = 0  # Задаем начальный индекс
        while (index + len_str <= len(words_indexes)):  # Идём по всей длине вектора индексов
            sample_list.append(words_indexes[index:index + len_str])  # "Откусываем" векторы длины len_str
            index += step  # Смещаеммся вперёд на step
        return sample_list

    # функция принимает последовательность индексов, размер окна, шаг окна
    def createTestMultiClasses(self, wordIndexes, xLen, step):
        # Создаём тестовую выборку из индексов
        x_test_01 = []  # Здесь будет список из всех классов, каждый размером "кол-во окон в тексте * 20000 (при maxWordsCount=20000)"
        x_test = []  # Здесь будет список массивов, каждый размером "кол-во окон в тексте * длину окна"(6 по 420*1000)
        for wI in wordIndexes:  # Для каждого тестового текста из последовательности индексов
            sample = (
                self.__splt_word_sequences(wI, xLen,
                                           step))  # Тестовая выборка размером "кол-во окон*длину окна"(например, 420*1000)
            x_test.append(sample)  # Добавляем в список
            x_test_01.append(self.tokenizer.sequences_to_matrix(
                sample))  # Трансформируется в Bag of Words в виде "кол-во окон в тексте * 20000"
        x_test_01 = np.array(x_test_01)  # И добавляется к нашему списку,
        x_test = np.array(x_test)  # И добавляется к нашему списку,

        return x_test_01, x_test  # функция вернёт тестовые данные: TestBag 6 классов на n*20000 и xTestEm 6 по n*1000


if __name__ == "__main__":
    # Загрука текущие новости
    # импортируем модуль по сбору новостей из RSS
    from rss_parser import ParseRSS
    rss = ParseRSS(config['ROLES_FEEDS'])
    feeds = rss.parse_feeds()
    news_df = rss.get_dataframe_feeds()
    # print(news_df.shape)

    # ПредОбработка текста
    # импортируем модуль по предварительной обработке текста rss лент
    from text_preprocessing import TextProcessing
    txt_proc = TextProcessing()
    news_df_preproc = txt_proc.preprocessing_df(news_df, columns=["description"])
    # print(news_df_preproc)

    # Прогнозирование
    predict_model = PredictNews()
    news_predict_df = predict_model.predict_from_df(news_df_preproc, columns=["description_preproc"])
    print(news_predict_df.sort_values(by=['predict', 'count_similar_words'], ascending=False))
    # Подлюкчать PredictNews во вне
    # Прогнозирование
    # from predict_model import PredictNews
