from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from models import Movietop
import os
import shutil
from datetime import datetime, timedelta
import jwt


SECRET_KEY = "simple-secret-key"
ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 1


app = FastAPI()


os.makedirs("static", exist_ok=True)
os.makedirs("static/img", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)


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
  <img src="/static/img/BGITU.jpg" alt="">
</body>
</html>"""


@app.get("/study", response_class=HTMLResponse)
def study_page():
    return HTML_STUDY


movies: list[Movietop] = [
    Movietop(name="Мир в огне", id=1, cost=0, director=""),
    Movietop(name="Лермонтов", id=2, cost=0, director=""),
    Movietop(name="Глазами пса", id=3, cost=0, director=""),
    Movietop(name="Горыныч", id=4, cost=0, director=""),
    Movietop(name="Финник 2", id=5, cost=0, director=""),
    Movietop(name="Алиса в Стране Чудес", id=6, cost=0, director=""),
    Movietop(name="Мажор в Дубае", id=7, cost=0, director=""),
    Movietop(name="Папины дочки. Мама вернулась", id=8, cost=0, director=""),
    Movietop(name="Детка на драйве", id=9, cost=0, director=""),
    Movietop(name="Сердцеед", id=10, cost=0, director=""),
]


added_movies = []


@app.get("/movietop/{movie_name}")
def get_movie(movie_name: str):
    for m in movies:
        if m.name.lower() == movie_name.lower():
            return m.model_dump()
    raise HTTPException(status_code=404, detail="Фильм не найден")


@app.get("/add-movie", response_class=HTMLResponse)
def add_movie_form():
    return """<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Добавить фильм</title>
</head>
<body>
    <form action="/add-movie" method="post" enctype="multipart/form-data">
        <p>Название: <input type="text" name="name" required></p>
        <p>Режиссер: <input type="text" name="director" required></p>
        <p>Бюджет: <input type="number" name="budget" required></p>
        <p><label><input type="checkbox" name="is_hit"> окупился?</label></p>
        <p>Описание фильма: <input type="file" name="description_file"></p>
        <p>Обложка фильма: <input type="file" name="cover_file" accept="image/*"></p>
        <p><input type="submit" value="Добавить фильм"></p>
    </form>
    <p><a href="/movies-with-photos">Посмотреть все фильмы с фото</a></p>
</body>
</html>"""


@app.post("/add-movie")
async def add_movie(
    name: str = Form(...),
    director: str = Form(...),
    budget: int = Form(...),
    is_hit: bool = Form(False),
    description_file: UploadFile = File(None),
    cover_file: UploadFile = File(None)
):
    movie_id = len(movies) + len(added_movies) + 1

    description_path = None
    cover_path = None

    if description_file and description_file.filename:
        description_path = f"static/uploads/desc_{movie_id}_{description_file.filename}"
        with open(description_path, "wb") as f:
            shutil.copyfileobj(description_file.file, f)

    if cover_file and cover_file.filename:
        cover_path = f"static/uploads/cover_{movie_id}_{cover_file.filename}"
        with open(cover_path, "wb") as f:
            shutil.copyfileobj(cover_file.file, f)

    new_movie = {
        "id": movie_id,
        "name": name,
        "director": director,
        "budget": budget,
        "is_hit": is_hit,
        "description_file": description_path,
        "cover_file": cover_path
    }

    added_movies.append(new_movie)

    return {"message": "Фильм добавлен!", "movie": new_movie}


@app.get("/movies-with-photos", response_class=HTMLResponse)
def movies_with_photos():
    html = """<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Фильмы с фото</title>
</head>
<body>
    <h1>Все фильмы с фотографиями</h1>
    <p><a href="/add-movie">Добавить новый фильм</a></p>
"""

    for movie in added_movies:
        html += f"""
    <div>
        <h3>{movie['name']}</h3>
        <p><strong>Режиссер:</strong> {movie['director']}</p>
        <p><strong>Бюджет:</strong> {movie['budget']}</p>
        <p><strong>Хит сезона:</strong> {'Да' if movie['is_hit'] else 'Нет'}</p>
"""
        if movie["cover_file"]:
            html += f'        <p><img src="/{movie["cover_file"]}"></p>'
        if movie["description_file"]:
            html += f'        <p><a href="/{movie["description_file"]}">Скачать описание</a></p>'
        html += "    </div>"

    if not added_movies:
        html += "<p>Пока нет добавленных фильмов с фото.</p>"

    html += """
</body>
</html>"""

    return html


@app.get("/add_film/{token}", response_class=HTMLResponse)
def add_film_form(token: str):
    return f"""<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Добавить фильм (JWT)</title>
</head>
<body>
    <h1>Добавить фильм (JWT)</h1>
    <form action="/add_film/{token}" method="post">
        <p>Название: <input type="text" name="name" required></p>
        <p>Режиссер: <input type="text" name="director" required></p>
        <p>Бюджет: <input type="number" name="budget" required></p>
        <p><label><input type="checkbox" name="is_hit"> окупился?</label></p>
        <p><input type="submit" value="Добавить фильм"></p>
    </form>
</body>
</html>"""


@app.post("/add_film/{token}")
async def add_film(
    token: str,
    name: str = Form(...),
    director: str = Form(...),
    budget: int = Form(...),
    is_hit: bool = Form(False)
):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    movie_id = len(movies) + len(added_movies) + 1

    new_movie = {
        "id": movie_id,
        "name": name,
        "director": director,
        "budget": budget,
        "is_hit": is_hit,
        "description_file": None,
        "cover_file": None
    }

    added_movies.append(new_movie)

    return {"message": "Фильм добавлен через JWT", "movie": new_movie}


@app.get("/login", response_class=HTMLResponse)
def login_form():
    return """<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Вход</title>
</head>
<body>
    <h1>Вход</h1>
    <form action="/login" method="post">
        <p>Логин: <input type="text" name="username"></p>
        <p>Пароль: <input type="password" name="password"></p>
        <p><input type="submit" value="Войти"></p>
    </form>
</body>
</html>"""


@app.post("/login")
async def login(
    request: Request,
    username: str = Form(None),
    password: str = Form(None)
):
    if username is None or password is None:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")

    if username == "user" and password == "123":
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
        jwt_data = {"sub": username, "exp": expire}
        jwt_token = jwt.encode(jwt_data, SECRET_KEY, algorithm=ALGORITHM)
        return {"message": "Login successful", "token": jwt_token}
    return {"message": "Invalid credentials"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8165, reload=True)
