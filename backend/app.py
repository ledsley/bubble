import mysql.connector
from mysql.connector import connect, Error, MySQLConnection
from collections import namedtuple
import sqlite3
import os
import re
from math import *
from flask import Flask, render_template, url_for,  request, flash, session, redirect, abort, g
from FDataBase import FDataBase
from UserLogin import UserLogin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_login import UserMixin, login_user

app = Flask(__name__)
app.config['SECRET_KEY'] ='dsajlsahds78dasda54cf'

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)

#========================= База Данных SQLite3 ==============================

def connect_db():
    # Подключение к базе данных
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin_sfedu",  # Замените на свой пароль
        database="g-portal",
    )
    conn.row_factory = lambda cursor, row: namedtuple('Row', [x[0] for x in cursor.description])(*row)
    return conn

def create_database():
    # Вспомогательная функция для создания таблиц базы данных
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    # Соединение с базой данных, если оно ещё не установлено
    if not hasattr(g,'link_db'):
        g.link_db = connect_db()
    return g.link_db

dbase = None
@app.before_request
def before_request():
    # Установление соединения с базой данных перед выполнением запроса
    global dbase
    db = get_db()
    dbase = FDataBase(db)

@app.teardown_appcontext
def close_db(error):
    # Закрываем соединение с базой данных, если оно было установлено
    if hasattr(g,'link_db'):
        g.link_db.close()

#============================================================================


#========================Проверка данных регистрации=========================
def is_valid_name(name):
    #Проверяет, является ли имя допустимым.

    pattern = r"^[A-ZА-ЯЁ]+[\sa-zA-Zа-яёА-ЯЁ]+$"
    return bool(re.match(pattern, name))

# Условия проверки фамилии
def is_valid_surname(surname):
    #Проверяет, является ли фамилия допустимой.

    pattern = r"^[A-ZА-ЯЁ]+[\sa-zA-Zа-яёА-ЯЁ]+$"
    return bool(re.match(pattern, surname))

# Условия проверки отчества
def is_valid_patronymic(patronymic):
    #Проверяет, является ли отчество допустимым.

    pattern = r"^[A-ZА-ЯЁ]+[\sa-zA-Zа-яёА-ЯЁ]+$"
    return bool(re.match(pattern, patronymic))

# Условия проверки логина
def is_valid_login(login):
    #Проверяет, является ли логин допустимым.

    pattern = r"^[a-zA-Z0-9]+[\sa-zA-Z0-9]+$"
    return bool(re.match(pattern, login))


# Условия проверки email
def is_valid_email(email):
    #Проверяет, является ли адрес электронной почты допустимым.

    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))

# Условия проверки пароля
def is_valid_password(password):
    #Проверяет, является ли пароль допустимым.

    # Минимальная длина пароля
    min_length = 8

    # Пароль должен содержать как минимум одну цифру
    has_number = any(char.isdigit() for char in password)

    # Пароль должен содержать как минимум одну строчную букву
    has_lowercase = any(char.islower() for char in password)

    # Пароль должен содержать как минимум одну прописную букву
    has_uppercase = any(char.isupper() for char in password)

    # Пароль должен содержать как минимум один специальный символ
    has_special_char = any(char in "!@#$%^&*()" for char in password)

    return len(password) >= min_length and has_number and has_lowercase and has_uppercase and has_special_char
#============================================================================


#======================= Структура меню навигации ===========================

menu = [
    {
        'name': 'Главная',
        'url': 'index',
    },
    {
        'name': 'Проверка квалификации',
        'url': 'qualification_check',
    },

    #{
    #    'name': 'Задонатить',
    #    'url': 'gratitude',
    #},
    {
        'name': 'Курсы',
        'url': 'contest',
    },
    {
        'name': 'Авторизация',
        'url': 'login',
    },
]

#============================================================================


#===============================Страницы сайта===============================


# ============================= Главная странца =============================
@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html', title = 'Главная страница сайта', menu = get_menu())

# ===================== Страница проверки квалификации ======================
@app.route('/qualification-check')
def qualification_check():
    return render_template('qualification-check.html', title = 'Проверка квалификации', menu = get_menu())

# =========================== Страница задонатить ===========================
'''@app.route('/gratitude')
def gratitude():
    return render_template('gratitude.html', title = 'Задонатить', menu = get_menu())'''

# ============================ Страница курсов ==============================

@app.route('/contest' , methods = ['GET', 'POST'])
def contest():
    if request.method == 'POST':
        course_name = request.form['name']
        course_theme = request.form['theme']
        course_points = request.form['points']

        dataBase = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="1111",
            database="project"
        )

        cursorObject = dataBase.cursor()

        sql= """
        INSERT INTO courses
        (name, theme, points)
        VALUES ( %s, %s, %s )
        """
        val = [(course_name, course_theme, course_points)]

        cursorObject.executemany(sql, val)
        dataBase.commit()

        dataBase.close()
        return redirect('/contest')
    else:
        return render_template('contest.html', title='Курсы', menu=get_menu())

#====================================доступные курсы============================================
@app.route("/open_courses")
def open_courses():
    dataBase = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="1111",
        database="project"
    )

    cursorObject = dataBase.cursor()

    query = "SELECT NAME, theme FROM courses where id = 1"
    cursorObject.execute(query)

    results = cursorObject.fetchall()

    for x in results:
        print(x)

    dataBase.close()
    return render_template('open_courses.html', results = results)

# ========================== Лидерборд ============================

@app.route("/leaderboard")

def leaderboard():
    dataBase = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="1111",
        database="project"
    )

    cursorObject = dataBase.cursor()

    query = ("delete from leaderboard ")
    cursorObject.execute(query)

    dataBase.commit()

    dataBase.close()

    dataBase = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="1111",
        database="project"
    )

    cursorObject = dataBase.cursor()

    query = ("INSERT INTO leaderboard(user_id,points) SELECT  id,progress from users order by progress desc limit 10 ")
    cursorObject.execute(query)

    dataBase.commit()

    dataBase.close()

    dataBase = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="1111",
        database="project"
    )

    cursorObject = dataBase.cursor()

    query = "select name,surname,patronymic,points from users join leaderboard on users.id = leaderboard.user_id where progress >0;"
    cursorObject.execute(query)

    results = cursorObject.fetchall()

    for x in results:
        print(x)

    dataBase.close()

    return render_template('leaderboard.html', results = results)

# ========================== Страница авторизации ============================
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        if "psw" in request.form:
            # Авторизация
            user = dbase.getUserByLogin(request.form.get('login'))
            if user and check_password_hash(user[6], request.form['psw']):
                userlogin = UserLogin().create(user)
                rm = True if request.form.get('remainme') else False
                login_user(userlogin, remember=rm)
                return redirect(url_for('profile'))
            else:
                flash('Неверная пара логин/пароль', 'error')
        else:
            print ("В регистрацию попал\n")
            print (is_valid_name(request.form['name']))
            print (is_valid_surname(request.form['surname']))
            print (is_valid_patronymic(request.form['patronymic']))
            print (is_valid_login(request.form['login']))
            print (is_valid_email(request.form['email']))
            # Регистрация
            if is_valid_name(request.form['name']) and is_valid_surname(request.form['surname']) and is_valid_patronymic(request.form['patronymic']) and is_valid_login(request.form['login']) and is_valid_email(request.form['email']) and is_valid_password(request.form['psw1']) and request.form['psw1'] == request.form['psw2']:
                hash = generate_password_hash(request.form['psw1'])
                res = dbase.addUser(request.form['name'], request.form['surname'], request.form['patronymic'], request.form['login'], request.form['email'], hash, 'user')
                if res:
                    flash('Пользователь успешно зарегистрирован', "success")
                    return redirect(url_for('login'))
                else:
                    flash('Пользователь с таким логином или email уже существует.', "error")
            else:
                flash('Неправильно введены данные!', "error")

    return render_template("login.html", menu=menu, title="Авторизация")

 
    return render_template("login.html", menu=menu, title="Авторизация")

# ======================== Страница после выхода ============================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))

# ========================== Страница профиля ===============================
@app.route("/profile/add_user", methods = ['POST', 'GET'])
def add_user():
    if request.method == 'POST':
        if is_valid_name(request.form['name']) and is_valid_surname(request.form['surname']) and is_valid_patronymic(request.form['patronymic']) and is_valid_login(request.form['login']) and is_valid_email(request.form['email']) and is_valid_password(request.form['psw1']) and request.form['psw1'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw1'])
            res = dbase.addUser(request.form['name'], request.form['surname'], request.form['patronymic'], request.form['login'], request.form['email'], hash, request.form['role'])
            if res:
                flash('Пользователь успешно зарегистрирован', "success")
                return redirect(url_for('profile'))
            else:
                flash('Пользователь с таким логином или email уже существует.', "error")
        else:
            flash('Неправильно введены данные!', "error")
    return render_template('add_user.html', title = 'Добавление пользователя', menu = get_menu())

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title = 'Профиль', menu = get_menu())


            
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title = 'Страница не найдена', menu = get_menu()), 404
@app.errorhandler(401)
def unauthorized(error):
    return render_template('page401.html', title = 'Вы не авторизованы', menu = get_menu()), 401
#============================================================================

def get_user_info():
    if current_user.is_authenticated:
        return current_user.get_name(), current_user.get_surname()
    else:
        return None
    
def get_menu():
    new_menu = menu[:-1].copy()
    user_info = get_user_info()
    if user_info:
        new_menu.append({
            'name': f'{user_info[0]} {user_info[1]}',
            'url': 'profile',
        })
    else:
        new_menu.append({
            'name': 'Авторизация',
            'url': 'login',
        })
    return new_menu

#=========================== Запуск веб-приложения ==========================

if __name__ == '__main__':
    app.run(debug=True)
    
#============================================================================
