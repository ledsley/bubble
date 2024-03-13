import mysql.connector
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
    
#========================= База Данных MySQL ================================

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

# Условия проверки никнейма
def is_valid_nickname(nickname):
    #Проверяет, является ли адрес электронной почты допустимым.

    pattern = r"^[a-zA-Z]+[\sa-zA-Z]+$"
    return bool(re.match(pattern, nickname))

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
        'name': 'Главная страница сайта',
        'url': 'main',
    },
    {
        'name': 'Проверка квалификации',
        'url': 'qualification-check',
    },
    {
        'name': 'Курсы',
        'url': 'сourses',
    },
    #{
    #    'name': 'Задонатить',
    #    'url': 'gratitude',
    #},
    {
        'name': 'Вход/Регистрация',
        'url': 'login',
    }]
        
#============================================================================


#===============================Страницы сайта===============================


# ============================= Главная странца =============================
@app.route('/main')
@app.route('/')
def main():
    return render_template('main.html', title = 'Главная страница сайта', menu = menu)

# ===================== Страница проверки квалификации ======================
@app.route('/qualification-check')
def qualification_check():
    return render_template('qualification-check.html', title = 'Проверка квалификации', menu = menu)

# ============================ Страница курсов ==============================
@app.route('/courses')
def courses():
    return render_template('courses.html', title = 'Курсы', menu = menu)

# =========================== Страница задонатить ===========================
'''@app.route('/gratitude')
def gratitude():
    return render_template('gratitude.html', title = 'Задонатить', menu = menu)'''

# ========================== Страница авторизации ============================
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = dbase.getUserByLogin(request.form.get('login'))
        if user and check_password_hash(user[6], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(url_for('profile'))
 
        flash('Неверная пара логин/пароль', 'error')
 
    return render_template("login.html", menu=menu, title="Авторизация")

# ========================== Страница регистрации ===========================
@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        if is_valid_name(request.form['name']) and is_valid_surname(request.form['surname']) and is_valid_patronymic(request.form['patronymic']) and is_valid_nickname(request.form['login']) and is_valid_email(request.form['email']) and is_valid_password(request.form['psw1']) and request.form['psw1'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw1'])
            res = dbase.addUser(request.form['name'], request.form['surname'], request.form['patronymic'], request.form['login'], request.form['email'], hash)
            if res:
                flash('Пользователь успешно зарегистрирован', "success")
                return redirect(url_for('login'))
            else:
                flash('Пользователь с таким логином или email уже существует.', "error")
        else:
            flash('Неправильно введены данные!', "error")
    return render_template('register.html', title = 'Регистрация', menu = menu)

# ======================== Страница после выхода ============================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('main'))

# ========================== Страница профиля ===============================
@app.route('/profile')
@login_required
def profile():
    return f"""<a href="{url_for('logout')}">Выйти из профиля</a><br><br>
                Текущий пользователь: {current_user.get_name()} {current_user.get_surname()}""" 

            
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title = 'Страница не найдена', menu = menu), 404
@app.errorhandler(401)
def unauthorized(error):
    return render_template('page401.html', title = 'Вы не авторизованы', menu = menu), 401
#============================================================================


#=========================== Запуск веб-приложения ==========================

if __name__ == '__main__':
    app.run(debug=True)

#============================================================================
