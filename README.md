# MORE Tech 4.0 Hackathon (2022)
https://moretech.vtb.ru/

## Track #2 DATA

[Презентация проекта](https://docs.google.com/presentation/d/1-7QbSZaMVCH64Q9TJK5ldbtWDmuQYdMR/edit?usp=sharing&ouid=113491937784577068477&rtpof=true&sd=true)

### Задача:
- Создать сервис, способный выделять из источников самые важные 2 3 новости и выделять тренды и инсайты в новостях 
- Провести анализ и сформировать выборку актуальных источников данных для двух бизнес ролей
- Реализовать выдачу релевантных новостей без дублирования текста, заложить возможность масштабирования ролей и добавления дополнительных источников данных

### Краткое описание проекта
1. Входные данные данных:
    - RSS-лент - для предсказаний актуальных новостей
    - Архив новостных RSS-лент - для обучение модели
    Использован архив новостей Лента.ру (2GB): [https://www.kaggle.com/datasets/yutkin/corpus-of-russian-news-articles-from-lenta]()
2. Обработка данных:

    2.1. Парсинг новостных rss-каналов для онлайн анализа свежих новостей. 
    
    2.2. Обработка архива новостей для обучения модели. Обработка осуществляется на основе данных о ключевых особенностей роли (по данным из конфигурационного файла)
    
    2.3. Обработка всех текстовых данных по правилам NLP (лемматизация, стоп-слов, стемминг и пр.)
3. Обучение модели. Использована нейронная сеть на базе TensorFlow решение через Bag of Words. Точность модели на валиадационных данных 85-90%
4. Прогноз релевантности новости к роли
5. Расчет новостных трендов 
7. Публикация релевантных новостей в телеграмм-канале [https://t.me/boohnews]()
6. Внешний API для доступа к релевантным новостям
8. Публикация релевантных новостей на web-странице



![MORE Tech 4 0 Hackathon drawio (2)](https://user-images.githubusercontent.com/115187419/194740278-2aa3d40b-a23c-42a8-92fd-cb2f9398b45c.png)

### Структура проекта
#### Файлы конфигурации 
В проекте реализован единый конфигурационный файл, в котором определены 
рабочие директории, характеристики роли (включая перечень rss каналов), 
константные значения, параметры модели.
- `config.json` -  единый конфигурационный файл
- `create_config.py` - скрипт отвечает за создание/обновление конфигурационного файла
- `requirements.txt` - перечень зависимостей (библиотеки необходимые для работы решения)
- `config.py` - конфигурация телеграм-бота (токен, ид-чата)

Данное решение позволяет очень просто масштабировать проект, за счет добавления списка rss-лент к ролям и изменнеие описания ролей за счет указания ключевых слов описывающих роль    
Достаточно в create_config.py добавить к роли дополнительный канал, он автоматически будет 
учитываться на всех этапах работы решения.


#### Модуль парсинга RSS-лент
- `rss_parser.py`
Модуль обеспечивет онлайн сбор новостей из публичных RSS-лент
Выполняемые функции: подключение к RSS-каналу, парсер данных, передача данных другим модулям. 
Масштабирование осущесвтляется в едином конфигурационном файле.
 

#### Модуль формирование Модели машинного обучения 
- `gen_train_data.py` - скрипт по генерации данных для обучения модели (разовый запуск)
- `create_model.py` - модуль по созданию модели и обучению модели и токенизатора
- `/models` - каталог содержащий обученную модель и обученный токенизатор
    - `model_more_tech_4.h5` - обученная модель
    - `tokenizer.pickle` - токенизатор используемый при обучении модели, необходим для обработки данных перед загрузкой в модель 

#### Модуль предварительной обработки текста новостей
- `text_preprocessing.py` - модуль выполняет следующий функционал: заполнение пропущенных данных, приведение текста к нижнему регистру, лемматизация (борьба с окончаниями), исключение стоп-слов, стемминг (обрезание окончаний, опциональный пункт обработки)

#### Модуль предварительной обработки текста новостей
- `predict_model.py`

#### Модуль публикации RSS-новостей в телеграм-канале проекта   
- `rss_tgbot.py` - модуль обеспечивет обработку новостного контента из rss-лент и публикацию в телеграм-канале [https://t.me/boohnews]() наиболее подходящих по заданным правилам новостей
- `util_functions.py` - модуль обеспечивает необходимый инструментарий управления телеграмм-каналом, включая подключение, асинхронную передачу данных и прочее

#### Модули расчета новостных трендов
- `get_trend.py` - поиск тренда с использованием инстурментов `trend_functions.py`
- `trend_functions.py` - реализация методов расчета тренда

#### Каталог dataset
Каталог `dataset/` содержит файлы в формате csv:
- `rss_dataset.csv` - результат работы модуля `rss_parser.py` - распарсинная лента новостей
- `union_train_data.csv` - сформирвоанный набор данных для обучение модели
- `booker.csv` - новости для публикации в телеграм-канале
- `done_link.csv` - сведения об опубликованных новостях в телеграм-канале
- `src_rss_archive/` - каталог для предобрабтоанных архивных данных исользуемых для обучения модели
    - `target_clear_mini_lenta_ru_news.csv` - пример предобрабтоанных данных. Датасет очищен от ошибок, сформирован целевой признак

#### API + WEB
- `main.py` - это модуль несущий функции веб сервера и REST сервера
- каталог `publoic/` - содержит веб-интерфейс

## Равзертывание
- Развертывание API + WEB -  файл main.py ствртует веб сервер и после доработок будет выполнять функцию ядра системы
- Развертывание ТГ-Бот - запусаешь файл rss_tgbot.py. Cоздаёте бота и канал в ТГ, добавляете бота в канал, все данные вносите в файл config.py
- Для АПИ важны следующие модули:
from rss_parser import ParseRSS (# импортируем модуль по сбору новостей из RSS)
from text_preprocessing import TextProcessing (# импортируем модуль по предварительной обработке текста rss лент) 
from predict_model import PredictNews (# Прогнозирование)


## Совместная работа 
Для совместной работы команды использованы следующие инстурменты:
- репозитарий GitHub - для совместной работой над разрабатываемым решением
- телеграмм-чат - для оперативных обсуждений
- zoom-комнаты - для голосовых обсуждений

GitHub Проекта: [https://github.com/MORETech4/Track_2_DATA]()



## Состав команды

- **Александр** - Капитан команды, аналитик, разработчик 
- **Иван** - Developer, Data Science, ML engineer
- **Екатерина** - Художник, визуализация
- **Евгений** - аналитик BI\DS, backend разработчик

### Шаги по улучшению решения
- добавить расчет "сложных" фичей: 
    - Локализация новости (город, регион, страна), 
    - Популярность новости (количество публикаций),
    - Эмоциональный окрас новости,
    - Информационные всплески (краткосрочные тренды)
- произвести обучение модели на большем кол-ве разнообразных данных
- настроить дообучение модели при получении новых данных
