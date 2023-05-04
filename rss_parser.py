"""
Модуль по сбору новостей из RSS
Модуль обеспечивает подключение rss-каналов
Масштабирование за счет добавление новых ролей с указанием тематических каналов.
"""

# TODO описать функции
# TODO сделать кодревью
# TODO добавить выгрузку за врменной период
# TODO уйти от необходмиости два раза указывать наименования колонок


import feedparser
import pandas as pd
from dateutil import parser
from datetime import datetime, timezone
import json

# Для конфигурации используется json
with open('config.json', 'r') as f:
    config = json.load(f)


class ParseRSS():
    # заголовок
    def __init__(self, roles_rss_feeds, is_log=False):
        self.roles_rss_feeds = roles_rss_feeds
        self.is_log = is_log
        self.feeds = None

    def parse_feeds(self):
        # Парсим ленты
        roles = []
        titles = []
        tags = []
        summary = []
        descriptions = []
        links = []
        published_dt = []
        published_ts = []

        for role_name, rss_feeds in self.roles_rss_feeds.items():
            if self.is_log:
                print(role_name)
            for url in self.roles_rss_feeds[role_name]["feeds"]:
                if self.is_log:
                    print(url)
                lenta = feedparser.parse(url)
                for item_news in lenta['items']:
                    roles.append(role_name)
                    titles.append(item_news['title'])
                    if tags in list(item_news.keys()):
                        tags.append(" ".join([x["term"] for x in item_news['tags']]))
                    else:
                        tags.append("")
                    if 'summary' in item_news and item_news['summary'] != "":
                        summary.append(item_news['summary'].strip())
                    else:
                        summary.append(item_news['title'].strip())
                    if 'description' in item_news and item_news['description'] != "":
                        descriptions.append(item_news['description'].strip())
                    else:
                        if 'summary' in item_news and item_news['summary'] != "":
                            descriptions.append(item_news['summary'].strip())
                        else:
                            descriptions.append(item_news['title'].strip())
                    links.append(item_news['link'])
                    if 'published' in item_news and item_news['published'] != "":
                        dt_publish = parser.parse(item_news['published'])
                    else:
                        dt_publish = datetime.now(timezone.utc).replace(microsecond=0)
                    # добавляем дату публикации
                    published_dt.append(dt_publish)
                    # Дату переводим в таймстеп
                    published_ts.append(dt_publish.timestamp())

        self.feeds = {"news_for_role": roles, "title": titles, "tags": tags, "summary": summary,
                      "description": descriptions,
                      "link": links, "published_dt": published_dt, "published_ts": published_ts}
        return self.feeds

    def get_feeds(self):
        return self.feeds

    def get_dataframe_feeds(self):
        df = pd.DataFrame.from_dict(self.feeds)
        return df

    def dataset_to_csv(self, feeds):
        """Формирует csv файл в формате Pandas с полями:
        'news_for_role' - поле отражающее для какой роли были собраны новости
        'title', 'tags', 'summary', 'description', 'link', 'published_dt' - атрибуты rss ленты
        """
        df = pd.DataFrame.from_dict(feeds)
        df.to_csv(config["RSS_FILENAME"], sep=";", encoding="utf-8-sig", header=True, index=True, index_label="id")
        return config["RSS_FILENAME"]


if __name__ == "__main__":
    rss = ParseRSS(config['ROLES_FEEDS'], is_log=True)
    feeds = rss.parse_feeds()
    rss.dataset_to_csv(feeds)
    print(rss.get_dataframe_feeds())
