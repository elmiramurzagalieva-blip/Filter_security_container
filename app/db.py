import mysql.connector
from datetime import datetime
import time
import os

DB_CONFIG = {
    'host': 'localhost',      # вместо 'mysql'
    'user': 'root',
    'password': '',           # пароль по умолчанию пустой
    'database': 'security_db'
}

def wait_for_db(max_retries=10, delay=3): #Ожидает готовности MySQL перед подключением
    for i in range(max_retries):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            conn.close()
            print("Подключение к MySQL успешно")
            return True
        except Exception as e:
            print(f"Попытка {i+1}/{max_retries}: MySQL не готов, ждём {delay} сек...")
            time.sleep(delay)
    print("MySQL не ответил после всех попыток")
    return False

def init_db(): #Создаёт таблицу logs при первом запуске
    if not wait_for_db():
        return
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp VARCHAR(50),
                user_ip VARCHAR(50),
                url TEXT,
                content_preview TEXT,
                decision VARCHAR(20),
                reason TEXT
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("База данных и таблица logs готовы")
    except Exception as e:
        print(f"Ошибка инициализации БД: {e}")

def save_log(url, content, decision, reason, user_ip="127.0.0.1"):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (timestamp, user_ip, url, content_preview, decision, reason)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_ip,
            url[:500] if url else "",
            (content[:200] + "...") if len(content) > 200 else content,
            decision,
            reason
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Ошибка сохранения лога: {e}")
        return False

def get_logs_from_db(limit=20):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT timestamp, user_ip, url, content_preview, decision, reason 
            FROM logs ORDER BY id DESC LIMIT %s
        ''', (limit,))
        logs = cursor.fetchall()
        cursor.close()
        conn.close()
        return logs
    except Exception as e:
        print(f"Ошибка получения логов: {e}")
        return []

def get_stats_from_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT COUNT(*) as count FROM logs WHERE decision = "ALLOWED"')
        allowed = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(*) as count FROM logs WHERE decision = "BLOCKED"')
        blocked = cursor.fetchone()['count']
        cursor.close()
        conn.close()
        return {"allowed": allowed, "blocked": blocked}
    except Exception as e:
        print(f"Ошибка получения статистики: {e}")
        return {"allowed": 0, "blocked": 0}
