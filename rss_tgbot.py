#!/usr/bin/env python3
# coding: utf-8
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
import spacy
import numpy as np
import csv

import asyncio
import traceback
import util_functions



def get_list_from_csv(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data


PATH_PROJECT = ""
DATASET_PATH = PATH_PROJECT + "dataset/"
RSS_FILENAME = DATASET_PATH + "rss_dataset.csv"
RSS_FILENAME2 = DATASET_PATH + "done_link.csv"

nlp = spacy.load("ru_core_news_lg")

class ParseRSS():
    # заголовок
    def __init__(self, roles_rss_feeds, done_links_list, is_log=True):
        self.roles_rss_feeds = roles_rss_feeds
        self.done_links_list=done_links_list
        self.is_log = is_log

    def test_news(self, link):
        if link not in self.done_links_list:
            return True
        else:
            return False

    def get_nouns_from_text(self, doc):
        nouns_list=list()
        for token in doc:
            if token.dep_ == "ROOT" or token.ent_iob==3 or (token.pos_ == 'NOUN'):
                nouns_list.append(token.lemma_)
        return nouns_list


    def parse_feeds(self):
        roles = []
        titles = []
        tags = []
        summary = []
        descriptions = []
        links = []
        published_dt = []

        for role_name, rss_feeds in self.roles_rss_feeds.items():
            if self.is_log:
                print(role_name)

            for url in rss_feeds:
                if self.is_log:
                    print(url)
                lenta = feedparser.parse(url)

                for item_news in lenta['items']:
                    if ParseRSS.test_news(self, item_news['link']):
                        print("news")
                        roles.append(role_name)
                        titles.append(item_news['title'])
                        tags.append(" ".join([x["term"] for x in item_news['tags']]))
                        doc=nlp(item_news['summary'])
                        nlist=ParseRSS.get_nouns_from_text(self, doc)
                        booker=util_functions.get_list_from_csv('dataset/booker.csv')
                        overlap = [x for x in nlist if x in booker[0]]
                        print(len(overlap), overlap)
                        if len(overlap) > 0:
                            post=util_functions.post_construct(
                                item_news['title'],
                                item_news['summary'],
                                len(overlap),
                                item_news['link']
                            )
                            loop = asyncio.get_event_loop()
                            reply_id = loop.run_until_complete(
                                util_functions.send_message(post)
                            )
                            print(item_news['title'], item_news['summary'])
                        summary.append(item_news['summary'])
                        descriptions.append(item_news['description'])
                        links.append(item_news['link'])
                        published_dt.append(parser.parse(item_news['published']))

        feeds = {"news_for_role": roles, "title": titles, "tags": tags, "summary": summary, "description": descriptions,
                 "link": links,
                 "published_dt": published_dt}
        return feeds

    def dataset_to_csv(self, feeds):
        """Формирует csv файл в формате Pandas с полями:
        'news_for_role' - поле отражающее для какой роли были собраны новости
        'title', 'tags', 'summary', 'description', 'link', 'published_dt' - атрибуты rss ленты
        """
        df = pd.DataFrame.from_dict(feeds)
        df.to_csv(RSS_FILENAME, sep=";", encoding="utf-8-sig", header=True, index=True, index_label="id")
        new_lnk=df["link"].tolist()
        print("nl",new_lnk)
        new_lnk.extend(self.done_links_list)

        df_lnk = pd.DataFrame(new_lnk)
        df_lnk.to_csv(RSS_FILENAME2, sep=";", encoding="utf-8-sig", header=True, index=True, index_label="id")
        return RSS_FILENAME


if __name__ == "__main__":

    df_dnlnlst=pd.read_csv('dataset/done_link.csv', sep=";", index_col=["id"])

    done_link_list=df_dnlnlst["0"].tolist()

    roles_rss_feeds = {"booker": ['https://lenta.ru/rss/', 'http://www.consultant.ru/rss/db.xml'],
                       "owner": ['https://www.kommersant.ru/RSS/news.xml', 'https://www.vesti.ru/vesti.rss']}
    rss = ParseRSS(roles_rss_feeds,done_link_list)
    feeds = rss.parse_feeds()
    rss.dataset_to_csv(feeds)
