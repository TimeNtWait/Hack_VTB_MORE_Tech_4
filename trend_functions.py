import feedparser
import pandas as pd
from dateutil import parser
from datetime import datetime, timezone
import spacy
import numpy as np
from urllib.parse import urlparse
from datetime import datetime, timedelta
import difflib

nlp = spacy.load("ru_core_news_lg")

stoplist=["банк","организация", "россия", "год", "сообщить", "господин", "г.", "-"]

all_rss_feeds=[
    'http://www.consultant.ru/rss/db.xml',
    'http://www.consultant.ru/rss/hotdocs.xml', # нет tags summary summary_detail
    "https://glavkniga.ru/rss/yandexnews",
    "https://minjust.gov.ru/ru/subscription/rss/events/",
    "https://ria.ru/export/rss2/archive/index.xml",    
    'https://www.kommersant.ru/RSS/news.xml', 
    'https://www.vesti.ru/vesti.rss',
    "https://vedomosti.ru/rss/articles",
    "https://vedomosti.ru/rss/news",
    "http://www.cbr.ru/rss/RssNews",
    'https://www.business-gazeta.ru/rss.xml'
]

def similarity(s1, s2):
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()


def get_domain(url):
    return urlparse('url').netloc


def get_nouns_from_text(doc):
        nouns_list=list()
        for token in doc:
            if token.dep_ == "ROOT" or token.ent_iob==3 or (token.pos_ == 'NOUN'):
                nouns_list.append(token.lemma_)
        return nouns_list
    
def get_trends(tred_words, stoplist, df_nouns):
    heads_dict=dict()
    for word in tred_words:
        if word not in stoplist:        
            headlines=df_nouns.loc[df_nouns["word"]==word]["title"].head(5).tolist()
            for c, item in enumerate(headlines):
                if c < len(headlines)-1:
                    if similarity(item, headlines[c+1]) < 0.5:
                        heads_dict[word]=[item, headlines[c+1]]
    return heads_dict

def parse_feeds():
    #roles = []
    titles = []
    tags = []
    summary = []
    descriptions = []
    links = []
    published_dt = []
    published_ts = []       
    for url in all_rss_feeds:            
        lenta = feedparser.parse(url)
        for item_news in lenta['items']:
            #roles.append(role_name)
            titles.append(item_news['title'])
            #print(item_news.keys())
            if tags in list(item_news.keys()):
                tags.append(" ".join([x["term"] for x in item_news['tags']]))
            else:
                tags.append("")
            if 'summary' in item_news and item_news['summary'] != "":
                summary.append(item_news['summary'])
            else:
                summary.append(item_news['title'])
            if 'description' in item_news and item_news['description'] != "":
                descriptions.append(item_news['description'])
            else:
                if 'summary' in item_news and item_news['summary'] != "":
                    descriptions.append(item_news['summary'])
                else:
                    descriptions.append(item_news['title'])
            links.append(item_news['link'])
            if 'published' in item_news and item_news['published'] != "":
                dt_publish = parser.parse(item_news['published'])
            else:
                dt_publish = datetime.now(timezone.utc).replace(microsecond=0)
            # добавляем дату публикации
            published_dt.append(dt_publish)
            # Дату переводим в таймстеп
            published_ts.append(dt_publish.timestamp())

    feeds = {"title": titles, "tags": tags, "summary": summary, "description": descriptions,
         "link": links, "published_dt": published_dt, "published_ts": published_ts}    
    
    return feeds


def get_trend_words(feeds):    
    df = pd.DataFrame.from_dict(feeds)
    df_nouns=pd.DataFrame(columns=['word', 'media','ts', 'link', "title","summary" ],dtype='object' )
    for c, i in enumerate(df['summary']):
        text_clean=i.replace("&nbsp;"," ").strip()
        doc=nlp(text_clean)
        list_of_nouns=get_nouns_from_text(doc)
        for noun in list_of_nouns:
            df_nouns.loc[len(df_nouns)] = [
                noun, 
                urlparse(df['link'].iloc[c]).netloc, 
                df['published_dt'].iloc[c],
                df['link'].iloc[c],
                df['title'].iloc[c],
                df['summary'].iloc[c]
            ] 
    df_nouns.ts=pd.to_datetime(df_nouns['ts'], utc=True)
    df_nouns['ts']=df_nouns['ts'].dt.tz_localize(None)
    df_nouns2=df_nouns.copy()
    df_nouns2=df_nouns2.drop(['link', "title","summary"], axis=1)
    df_nouns2['ts'] = pd.DataFrame([(x.hour) for x in df_nouns['ts']])
    df_hor=pd.pivot_table(df_nouns2, index=['word'], columns=['ts'], values=['word'], aggfunc='count', fill_value=0)
    df_hor['sum'] = df_hor.sum(axis=1)
    tred_words=df_hor.sort_values(by="sum", ascending=False).head(20).index.tolist()
    return(tred_words, df_nouns)