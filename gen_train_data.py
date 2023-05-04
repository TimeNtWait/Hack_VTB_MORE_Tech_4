"""
Скрипт по генерации данных для модели машинного обученияч
Формирование данных для обучения модели производиться ЕДИНОЖДЫ
!!!Данный срипт не предназначен для загрузи и использования в других программах
Рабочий скрипт, прилагается т.к. использовался для формирвоания данных
"""

import pandas as pd
# импортируем мдуль по предварительной обработке текста rss лент
from text_preprocessing import TextProcessing

import json

# Для конфигурации используется json
with open('config.json', 'r') as f:
    config = json.load(f)



# for lenta_ds_filename in ["clear_mini_lenta_ru_news.csv", "clear_mini_lenta_ru_news_2.csv"]:
# for lenta_ds_filename in ["clear_MICRO_lenta_ru_news.csv"]:
for lenta_ds_filename in []:
    print(lenta_ds_filename)
    lenta_df = pd.read_csv(config["LENTA_DATASET_PATH"] + lenta_ds_filename, sep=",", header=None,
                           names=["link", "title", "description", "summary", "tags", "published_date"])
    # ПредОбработка текста
    txt_proc = TextProcessing()
    lenta_df = txt_proc.preprocessing_df(lenta_df, columns=["description"])


    def is_include(text, role_keywords=[]):
        role_keywords = ["налог", "контролирующие органы", "МСФО", "юрлиц", "физлиц", "инспекция", "налоговик",
                         "налогоплательщик", "налоговый учет", "баланс", "бюджетирование", "ИФНС", "ПФР", "ФСС",
                         "ФОТ", ]
        role_keywords = [x.lower() for x in role_keywords]
        return sum([text.count(x) for x in role_keywords]) > 2


    good_tags = ['Деловой климат', 'Госэкономика', 'Социальная сфера', 'Общество', 'Бизнес', 'Рынки', 'Политика',
                 'Деньги', 'Экономика', 'Регионы', ]
    lenta_df["target"] = "unknow"
    mask = lenta_df['description_preproc'].apply(lambda x: is_include(x))
    lenta_df["target"] = np.where(mask & lenta_df["tags"].isin(good_tags), "booker", "unknow")

    find_positive_target = lenta_df[lenta_df["target"] == "booker"]
    count_find_target = find_positive_target.shape

    find_negative_target = lenta_df[~lenta_df["tags"].isin(good_tags)].sample(n=int(count_find_target[0] * 1.5))

    union_find_target = pd.concat([find_positive_target, find_negative_target], ignore_index=True)
    union_find_target.to_csv(LENTA_DATASET_PATH + "target_" + lenta_ds_filename, sep=";", encoding="utf-8-sig",
                             header=True, index=True, index_label="id")

#Объединиение рассчитаных данных
lenta_df_1 = pd.read_csv(config["LENTA_DATASET_PATH"] + "target_clear_mini_lenta_ru_news.csv", sep=";", skiprows=[0], names=["link","title","description","summary","tags","published_date","description_preproc","target",])
lenta_df_2 = pd.read_csv(config["LENTA_DATASET_PATH"] + "target_clear_mini_lenta_ru_news_2.csv", sep=";", skiprows=[0], names=["link","title","description","summary","tags","published_date","description_preproc","target",])
lenta_df_3 = pd.read_csv(config["LENTA_DATASET_PATH"] + "target_clear_mini_lenta_ru_news_3.csv", sep=";", skiprows=[0], names=["link","title","description","summary","tags","published_date","description_preproc","target",])
lenta_df_4 = pd.read_csv(config["LENTA_DATASET_PATH"] + "target_clear_mini_lenta_ru_news_4.csv", sep=";", skiprows=[0], names=["link","title","description","summary","tags","published_date","description_preproc","target",])
lenta_df_5 = pd.read_csv(config["LENTA_DATASET_PATH"] + "target_clear_mini_lenta_ru_news_5.csv", sep=";", skiprows=[0], names=["link","title","description","summary","tags","published_date","description_preproc","target",])
lenta_df_6 = pd.read_csv(config["LENTA_DATASET_PATH"] + "target_clear_mini_lenta_ru_news_6.csv", sep=";", skiprows=[0], names=["link","title","description","summary","tags","published_date","description_preproc","target",])
union_find_target = pd.concat([lenta_df_1, lenta_df_2, lenta_df_3, lenta_df_4, lenta_df_5, lenta_df_6], ignore_index=True)
print(union_find_target.shape)
# union_find_target.head(3)

# Генерируется исходный набор данных для обучения модели
union_find_target.to_csv(config["DATASET_PATH"] + "union_train_data.csv", sep=";", encoding="utf-8-sig",
                         header=True, index=True, index_label="id")