from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from models import Movietop
import os

app = FastAPI()

os.makedirs("static/img", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

HTML_STUDY = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Моё учебное заведение</title>
</head>
<body>
  <h1>БГИТУ</h1>
  <p>Город: Брянск</p>
  <p>Программа: ИВТ</p>
  <img src="/static/img/BGITU.jpg" alt="БГИТУ">
</body>
</html>"""

@app.get("/study", response_class=HTMLResponse)
def study_page():
    """Задание 2: Возвращает данные учебного заведения с фото"""
    return HTML_STUDY

movies: list[Movietop] = [
    Movietop(name="Мир в огне", id=1, cost=200000000, director="Режиссер 1"),
    Movietop(name="Лермонтов", id=2, cost=150000000, director="Режиссер 2"),
    Movietop(name="Глазами пса", id=3, cost=100000000, director="Режиссер 3"),
    Movietop(name="Горыныч", id=4, cost=180000000, director="Режиссер 4"),
    Movietop(name="Финник 2", id=5, cost=120000000, director="Режиссер 5"),
    Movietop(name="Алиса в Стране Чудес", id=6, cost=170000000, director="Режиссер 6"),
    Movietop(name="Мажор в Дубае", id=7, cost=90000000, director="Режиссер 7"),
    Movietop(name="Папины дочки. Мама вернулась", id=8, cost=80000000, director="Режиссер 8"),
    Movietop(name="Детка на драйве", id=9, cost=110000000, director="Режиссер 9"),
    Movietop(name="Сердцеед", id=10, cost=95000000, director="Режиссер 10"),
]

@app.get("/movietop/{movie_name}")
def get_movie(movie_name: str):
    """
    Задание 3.3: Возвращает JSON с данными о фильме
    Пример: /movietop/Мир в огне
    """
    for m in movies:
        if m.name.lower() == movie_name.lower():
            return m.model_dump()
    raise HTTPException(status_code=404, detail="Фильм не найден")

@app.get("/")
def root():
    """Главная страница"""
    return {
        "message": "FastAPI - Задание А",
        "endpoints": {
            "/study": "Информация об учебном заведении",
            "/movietop/{название}": "Данные о фильме из топ-10",
            "/docs": "API документация"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8165, reload=True)