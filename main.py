from fastapi import FastAPI, HTTPException, Form, Cookie, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from models import Movietop
from datetime import datetime, timedelta
import uuid

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

movies: list[Movietop] = [
    Movietop(name="Inception", director="Christopher Nolan", id=1, cost=160, is_available=True),
    Movietop(name="Interstellar", director="Christopher Nolan", id=2, cost=165, is_available=True),
    Movietop(name="The Matrix", director="Wachowski", id=3, cost=63, is_available=True),
    Movietop(name="Fight Club", director="David Fincher", id=4, cost=63, is_available=False),
    Movietop(name="Se7en", director="David Fincher", id=5, cost=33, is_available=True),
    Movietop(name="Avatar", director="James Cameron", id=6, cost=237, is_available=True),
    Movietop(name="Titanic", director="James Cameron", id=7, cost=200, is_available=True),
    Movietop(name="Gladiator", director="Ridley Scott", id=8, cost=103, is_available=True),
    Movietop(name="Joker", director="Todd Phillips", id=9, cost=55, is_available=True),
    Movietop(name="The Godfather", director="Francis Ford Coppola", id=10, cost=7, is_available=False),
]

sessions = {}

users = {
    "admin": "password123",
    "user": "pass123"
}

@app.post("/login")
async def login(
        username: str = Form(...),
        password: str = Form(...),
        response: Response = None
):
    if username not in users or users[username] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = str(uuid.uuid4())

    expiration_time = datetime.now() + timedelta(minutes=2)

    sessions[token] = {
        "username": username,
        "login_time": datetime.now(),
        "expiration_time": expiration_time
    }

    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        max_age=120
    )

    return {"message": "Login successful", "username": username}

@app.get("/login-form", response_class=HTMLResponse)
async def login_form():
    return """
    <html>
        <head><title>Вход в систему</title></head>
        <body>
            <h2>Вход в систему</h2>
            <form action="/login" method="post">
                <label>Имя пользователя:</label><br>
                <input type="text" name="username" required><br><br>

                <label>Пароль:</label><br>
                <input type="text" name="password" required><br><br>

                <button type="submit">Войти</button>
            </form>
            <br>
            <p>Тестовые учетные данные:</p>
            <p>Пользователь: <strong>admin</strong> Пароль: <strong>password123</strong></p>
            <p>Пользователь: <strong>user</strong> Пароль: <strong>pass123</strong></p>
        </body>
    </html>
    """

@app.get("/user")
async def get_user(session_token: str = Cookie(None), response: Response = None):
    if not session_token:
        return {"message": "Unauthorized"}

    if session_token not in sessions:
        return {"message": "Unauthorized"}

    session_data = sessions[session_token]
    current_time = datetime.now()

    if current_time > session_data["expiration_time"]:
        del sessions[session_token]
        return {"message": "Unauthorized"}

    new_expiration_time = current_time + timedelta(minutes=2)
    sessions[session_token]["expiration_time"] = new_expiration_time

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=120
    )

    return {
        "profile": {
            "username": session_data["username"],
            "login_time": session_data["login_time"].isoformat(),
            "current_time": current_time.isoformat(),
            "session_expires_at": new_expiration_time.isoformat()
        },
        "movies": [
            {
                "name": m.name,
                "director": m.director,
                "id": m.id,
                "cost": m.cost,
                "is_available": m.is_available
            }
            for m in movies
        ]
    }

@app.get("/study")
async def get_study():
    return {
        "name": "БГИТУ",
        "city": "Брянск",
        "address": "ул. Станке Димитрова 3",
        "website": "https://bgitu.ru",
        "photo": "/static/school.png"
    }

@app.get("/photo", response_class=HTMLResponse)
async def show_photo():
    return """
    <html>
        <head><title>Фото учебного заведения</title></head>
        <body>
            <h2>Учебное заведение: БГИТУ</h2>
            <img src="/static/school.png" alt="Фото БГИТУ" width="350">
        </body>
    </html>
    """

@app.get("/movietop/{movie_name}")
async def get_movie(movie_name: str):
    for m in movies:
        if m.name.lower() == movie_name.lower():
            return m
    raise HTTPException(status_code=404, detail="Movie not found")

@app.get("/add-movie-form", response_class=HTMLResponse)
async def add_movie_form():
    return """
    <html>
        <head><title>Добавить фильм</title></head>
        <body>
            <h2>Добавить новый фильм</h2>
            <form action="/add-movie" method="post" enctype="multipart/form-data">
                <label>Название фильма (текст):</label><br>
                <input type="text" name="name" required><br><br>

                <label>Режиссёр (текст):</label><br>
                <input type="text" name="director" required><br><br>

                <label>Стоимость в млн $ (число):</label><br>
                <input type="number" name="cost" required><br><br>

                <label>Доступен для проката (логическое):</label><br>
                <input type="checkbox" name="is_available" checked><br><br>

                <label>Обложка фильма (файл изображения):</label><br>
                <input type="file" name="cover" accept="image/*"><br><br>

                <button type="submit">Добавить фильм</button>
            </form>
            <br>
            <a href="/movies-list">Посмотреть все фильмы</a>
        </body>
    </html>
    """

@app.post("/add-movie")
async def add_movie(
        name: str = Form(...),
        director: str = Form(...),
        cost: int = Form(...),
        is_available: bool = Form(False),
        cover=None
):
    from pathlib import Path
    import shutil

    new_id = max([m.id for m in movies]) + 1 if movies else 1

    cover_path = ""
    if cover:
        file_path = Path("static") / cover.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(cover.file, buffer)
        cover_path = f"/static/{cover.filename}"

    new_movie = Movietop(
        name=name,
        director=director,
        id=new_id,
        cost=cost,
        is_available=is_available,
        cover=cover_path
    )

    movies.append(new_movie)

    return {"message": "Фильм добавлен", "movie": new_movie}

@app.get("/movies-list", response_class=HTMLResponse)
async def movies_list():
    html = """
    <html>
        <head><title>Список фильмов</title></head>
        <body>
            <h2>Все фильмы</h2>
    """

    for movie in movies:
        html += f"""
        <div style="border: 1px solid #ccc; padding: 10px; margin: 10px 0;">
            <h3>{movie.name}</h3>
            <p><strong>Режиссёр:</strong> {movie.director}</p>
            <p><strong>Стоимость:</strong> ${movie.cost} млн</p>
            <p><strong>Доступен:</strong> {'Да' if movie.is_available else 'Нет'}</p>
        """

        if movie.cover:
            html += f'<img src="{movie.cover}" alt="{movie.name}" width="200"><br>'

        html += "</div>"

    html += """
            <br>
            <a href="/add-movie-form">Добавить новый фильм</a>
        </body>
    </html>
    """

    return html
