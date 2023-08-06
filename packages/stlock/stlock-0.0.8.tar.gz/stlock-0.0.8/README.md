Библиотека для сервиса авторизации **STLock** *(powered by **SmartTechnoLab**)*

**Статус:** *В разработке*

# Библиотека Python STLock


# Быстрый старт
Пример с библиотекой FastAPI


```shell
pip install stlock
pip install fastapi
pip install uvicorn
```

main.py:
```python
from fastapi import FastAPI, HTTPException, Body, Query
from stlock import AuthClient

# создание экземпляра класса
AC = AuthClient(
    client_id="client",  # id клиента
    client_secret="secret",  # secret клиента
    code_redirect_uri="http://localhost:8000/code",  # ссылка перенаправления запроса с кодом
    service_endpoint="https://bbac70hrtmfdqn5drnga.containers.yandexcloud.net",  # ссылка на сервис авторизации
)

# service_endpoint="https://bbac70hrtmfdqn5drnga.containers.yandexcloud.net"
# dev версия проекта, очищается каждые 24 часа

app = FastAPI()


# Регистрация пользователя
@app.post("/register", status_code=201)
def register_user(username=Body(...), password=Body(...)):
   data, status_code = AC.register(username, password)
   if status_code >= 400:
       raise HTTPException(status_code, data["detail"])
   return data


# Авторизация пользователя, редирект на http://localhost:8000/code
@app.post('/login')
def login(username: str = Body(...), password: str = Body(...)):
   data, status_code = AC.authorize_user(username, password)
   if status_code >= 400:
       raise HTTPException(status_code, data["detail"])
   return data


# Получение кода после редиректа, заполняется в code_redirect_uri
@app.get('/code')
def getcode(code=Query(None)):
   data, status_code = AC.get_tokens(code)
   if status_code >= 400:
       raise HTTPException(status_code, data["detail"])
   return data


# Обмен refresh токена но новые refresh и access токены
@app.post("/refresh")
def do_refresh_token(refresh_token=Body(...)):
    data, status_code = AC.do_refresh(refresh_token['refresh_token'])
    print(data, status_code)
    if status_code >= 400:
        raise HTTPException(status_code, data["detail"])
    return data


# Получение информации из токена
@app.get("/user")
def get_user_info(token: str = Query(...)):
    user_data = AC.decode(token)
    return user_data
```

Для запуска сервера:
```
uvicorn main:app
```

# Описание методов:

```python
def register(username: str, password: str) -> (dict, int):
```

*Создаёт нового пользователя в базе данных*

###### Пример использования:
```python
@app.post("/register", status_code=201)
def register_user(username=Body(...), password=Body(...)):
   data, status_code = AC.register(username, password)
   if status_code >= 400:
       raise HTTPException(status_code, data["detail"])
   return data
```

###### Создание пользователя:

Input:
```
POST http://localhost:8000/register
Body {
    "username": "user1",
    "password": "Password123!"
}
```

Output:
```json
{
    "detail": "User registred"
}
```

---

```python
def authorize_user(username: str, password: str) -> (dict, int):
```

*Авторизирует запрос на логин пользователя, перенаправляет на страницу с кодом в query запросе*

###### Пример использования:

```python
@app.post('/login')
def login(username: str = Body(...), password: str = Body(...)):
   data, status_code = AC.authorize_user(username, password)
   if status_code >= 400:
       raise HTTPException(status_code, data["detail"])
   return data
```

###### Авторизация пользователя:

Input:
```
POST http://localhost:8000/login
Body {
    "username": "user1",
    "password": "Password123!"
}
```

Output:
```json
{
    "access_token": "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJjbGllbnQiLCJleHAiOjE2ODQ4NTgzNzgsInN1YiI6ImQ5YjBmYjE1LWJjYmQtNDNkNy1hMDdlLTAxNTIwMjBlZWI2ZiIsInJvbGUiOiJUZXN0In0.5_CHG7IR0DDulJcaPF8owduWsVsI2a5Vvbx-gyG_Xi2JIs9tpaPfJircy8WZXkeZ_3Mk8tAuvaxhTn7ytWXtdA",
    "expires_in": 60,
    "refresh_token": "MJFMYZGWNWQTNDA5MI01NTU0LTHIMMYTYTI4MJM0MTZKMJHM",
    "token_type": "Bearer"
}
```

---

```python
def get_tokens(code: str) -> (dict, int):
```

*Выдаёт токены пользователя (access, refresh)*

###### Пример использования:

```python
@app.get('/code')
def getcode(code=Query(None)):
   data, status_code = AC.get_tokens(code)
   if status_code >= 400:
       raise HTTPException(status_code, data["detail"])
   return data
```

---

```python
def decode(token) -> dict:
```

*Декодирует токен, возвращает словарь с данными о пользователе*

###### Пример использования:

```python
@app.get("/user")
def get_user_info(token: str = Query(...)):
    user_data = AC.decode(token)
    return user_data
```

###### Получение информации о пользователе:

Input:
```
GET http://localhost:8000/user?token=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJjbGllbnQiLCJleHAiOjE2ODQ4NTgzNzgsInN1YiI6ImQ5YjBmYjE1LWJjYmQtNDNkNy1hMDdlLTAxNTIwMjBlZWI2ZiIsInJvbGUiOiJUZXN0In0.5_CHG7IR0DDulJcaPF8owduWsVsI2a5Vvbx-gyG_Xi2JIs9tpaPfJircy8WZXkeZ_3Mk8tAuvaxhTn7ytWXtdA
```

Output:
```json
{
    "aud": "client",
    "exp": 1684858378,
    "sub": "d9b0fb15-bcbd-43d7-a07e-0152020eeb6f",
    "role": "Test"
}
```

---

```python
def do_refresh(token: str) -> (dict, int):
```

*Обменивает refresh token на новый access и refresh токены*

###### Пример использования:

```python
@app.post("/refresh")
def do_refresh_token(refresh_token=Body(...)):
    data, status_code = AC.do_refresh(refresh_token['refresh_token'])
    print(data, status_code)
    if status_code >= 400:
        raise HTTPException(status_code, data["detail"])
    return data
```

###### Обновление токена:

Input:
```
POST http://localhost:8000/refresh
Body {
    "refresh_token": "MJFMYZGWNWQTNDA5MI01NTU0LTHIMMYTYTI4MJM0MTZKMJHM"
}
```

Output:
```json
{
    "access_token": "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJjbGllbnQiLCJleHAiOjE2ODQ4NTg0MzgsInN1YiI6ImQ5YjBmYjE1LWJjYmQtNDNkNy1hMDdlLTAxNTIwMjBlZWI2ZiIsInJvbGUiOiJUZXN0In0.5hFJg-U6i9E9GFp0Gxsn9ME3Dy-JtqKEyZotHT7WmnAsdZeLrDBjDU20ttb5f5HMLep8SWruTOoWjlfiZuGBKg",
    "expires_in": 60,
    "refresh_token": "NTC1ZDY5YJYTZTC0MC01ZJRMLTHJZTUTY2E1MMFJMTAZNZI0",
    "token_type": "Bearer"
}
```