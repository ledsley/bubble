import mysql.connector
import datetime
import math
import time
class FDataBase:
    def __init__(self, db):
        self.db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = "SELECT * FROM mainmenu"
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из Базы Данных")
        return []
    
    def addUser(self, name, surname, patronymic, login, email, hpsw, role):
            try:
                # Проверка существования пользователя по логину
                self.__cur.execute("SELECT COUNT(*) FROM users WHERE login=%s", (login,))
                res_login = self.__cur.fetchone()
                if res_login[0] > 0:
                    print("Пользователь с таким login уже зарегистрирован")
                    return False

                # Проверка существования пользователя по email
                self.__cur.execute("SELECT COUNT(*) FROM users WHERE email=%s", (email,))
                res_email = self.__cur.fetchone()
                if res_email[0] > 0:
                    print("Пользователь с таким email уже зарегистрирован")
                    return False


                # Добавление пользователя
                self.__cur.execute("INSERT INTO users (id, name, surname, patronymic, login, email, psw, role, progress, achivments) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, NULL, %s)", (name, surname, patronymic, login, email, hpsw, role, "Нет"))

                # Сохранение изменений
                self.db.commit()
            except mysql.connector.Error as e:
                print("Ошибка при добавлении пользователя:" + str(e))
                return False

            return True

    
    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id={user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False 
 
            return res
        except mysql.connector.Error as e:
            print("Ошибка получения данных из БД:"+str(e))
 
        return False    
    def getUserByLogin(self, login):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE login='{login}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False 
 
            return res
        except mysql.connector.Error as e:
            print("Ошибка получения данных из БД:"+str(e))
 
        return False    

