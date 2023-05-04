"""
скрипт мини REST сервера
"""

""" Загружаем необходимые пакеты"""
import uuid
from fastapi import FastAPI, Body, status
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi import Query, Response
from fastapi.staticfiles import StaticFiles 



#'title', 'summary', 'description', 'tags', 'link', 'published_dt'

"""Клас описывающий структуру новости"""
class News:
    def __init__(self, role, title, summary, description, link, published_dt):
        self.role = role
        self.title = title
        self.summary = summary
        self.description = description
        self.link = link
        self.published_dt = published_dt
        self.id = str(uuid.uuid4())
# мокап данные
news_1 = [
            News("booker",
            "Предварительно определены коэффициенты-дефляторы на 2023 год", 
            "Подготовлен проект приказа, устанавливающего значения коэффициентов-дефляторов на 2023 год", 
            "Подготовлен проект приказа, устанавливающего значения коэффициентов-дефляторов на 2023 год.",
            "https://glavkniga.ru/news/14337;2022-10-05",
            "2022-10-05 13:12:04+04:00"
            ), 
            News("Правила заполнения платежек решили полностью переписать",
            "Поскольку с 2023 года перечислять налоги и взносы организации и ИП будут через механизм единого налогового платежа (ЕНП), изменятся правила заполнения платежек.",
            "Поскольку с 2023 года перечислять налоги и взносы организации и ИП будут через механизм единого налогового платежа (ЕНП), изменятся правила заполнения платежек. В связи с этим Минфин планирует вовсе отменить приказ от 12.11.2013 № 107н и утвердить новый.",
            "https://login.consultant.ru/link/?req=doc;base=LAW;n=381045;dst=1000000001","2022-10-06 09:16:00+04:00")

        ]

def find_news(id):
    for news in news_1:
        if news.id == id:
            return news
    return None

app = FastAPI()

@app.get("/")
async def main():
    return FileResponse("public/index.html")

@app.get("api/get_news")
def get_news():
    return news_1

@app.get("api/news/{id}")
def get_target_news(id):
    # получаем новость по id
    news_1 = find_news
    print(news_1)
    if news_1==None:
        return JSONResponse(status_code = status.HTTP_404_NOT_FOUND, content = {"message":"Новости отсутствуют"}
        )
    return news_1

@app.delete("api/news/{id}")
def delete_news(id):
    news_1 = find_news(id)

    if news_1 == None:
        return JSONResponse(
            status_code = status.HTTP_404_NOT_FOUND,
            content = {"message":"Новость не найдена"}
        )
    news_1.remove(news_1)
    return news_1
