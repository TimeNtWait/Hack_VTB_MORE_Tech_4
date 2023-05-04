"""Модуль по предварительной обработке текста rss лент
Включая следующие виды обрабатки:
- заполнение пропущенных данных
- приведение текста к нижнему регистру
- лемматизация - боримся с окончаниями
- убираем стоп-слова
- стемминг - обрезаем окончания (опционально)
"""
import pandas as pd
import re
import nltk
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')
import pymorphy2


class TextProcessing():
    """
    Делаем следующую обрабатку текста:
    - downcase
    - лемматизация - боримся с окончаниями
    - убираем стоп-слова
    - стемминг - обрезаем окончания (опционально)
    """

    def __init__(self):
        # лемматизация
        self.morph = pymorphy2.MorphAnalyzer()
        # стемминг
        self.snowball = SnowballStemmer(language="russian")
        # стоп-слова
        self.rus_stopwords = stopwords.words("russian")

    def preprocessing_text(self, text):
        # приводим к нижнему регистру
        text = text.lower()
        # убираем стоп слова
        text = " ".join([w for w in re.findall(r"\w+", text) if w not in rus_stopwords])
        # лемматизация
        text = " ".join([self.morph.parse(w)[0].normal_form for w in text.split(' ')])
        # стемминг
        text = " ".join([self.snowball.stem(w) for w in text.split(' ')])
        return text

    def preprocessing_df(self, df, columns=["description", "title", "summary"], enable_stemming=False):
        self.df = df
        # Заполняем пустые значениям описания заголовком статьи
        self.fillna_columns()
        for column_name in columns:
            self.preprocessing_series(column=column_name, enable_stemming=enable_stemming)
        return self.df

    def fillna_columns(self):
        df = self.df

        # Для случаев когда summary пустой заполняем description
        df["summary"] = df["summary"].fillna(df["description"])
        # Для случаев когда summary пустой заполняем title
        # Для случаев когда и description пустой использеум title
        df["summary"] = df["summary"].fillna(df["title"])
        df["description"] = df["description"].fillna(df["summary"])
        df["title"] = df["title"].fillna(df["summary"])

    def preprocessing_series(self, column, enable_stemming=False):
        # приводим к нижнему регистру
        self.df[f"{column}_preproc"] = self.lower_text(self.df[column])
        # убираем стоп слова
        self.df[f"{column}_preproc"] = self.stopwords(self.df[f"{column}_preproc"])
        # лемматизация
        self.df[f"{column}_preproc"] = self.lemmatization(self.df[f"{column}_preproc"])
        # стемминг
        if enable_stemming:
            self.df[f"{column}_preproc"] = self.stemming(self.df[f"{column}_preproc"])

    def lower_text(self, series):
        # приводим к нижнему регистру
        return series.str.lower()

    def stopwords(self, series):
        lemma_series = series.apply(
            lambda x: " ".join([w for w in re.findall(r"\w+", x) if w not in self.rus_stopwords]))
        return lemma_series

    def lemmatization(self, series):
        # лемматизация
        lemma_series = series.apply(lambda x: " ".join([self.morph.parse(w)[0].normal_form for w in x.split(' ')]))
        return lemma_series

    def stemming(self, series):
        # стемминг
        stemm_series = series.apply(lambda x: " ".join([self.snowball.stem(w) for w in x.split(' ')]))
        return stemm_series


if __name__ == "__main__":
    import pandas as pd
    import json

    # Для проверки используем данные новостных лент из csv
    with open('config.json', 'r') as f:
        config = json.load(f)
    news_df = pd.read_csv(config["RSS_FILENAME"], sep=";", index_col=["id"])

    # ПредОбработка текста
    txt_proc = TextProcessing()
    lenta_df = txt_proc.preprocessing_df(news_df, columns=["description"])
    print(lenta_df)
