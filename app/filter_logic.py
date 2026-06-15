import re
from datetime import datetime
from prometheus_client import Histogram, Counter, Gauge, generate_latest, REGISTRY

# Время выполнения функции analyze() - гистограмма
analysis_duration = Histogram(
    'analysis_duration_ms',
    'Время выполнения функции analyze() в миллисекундах',
    buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000]
)
# Счетчик блокировок по типам
blocked_by_blacklist = Counter('blocked_by_blacklist_total', 'Блокировки по BLACKLIST')
blocked_by_patterns = Counter('blocked_by_patterns_total', 'Блокировки по PATTERNS')
total_requests = Counter('total_requests_total', 'Всего запросов')

# Текущий балл риска (последний)
current_risk_score = Gauge('current_risk_score', 'Последний вычисленный балл риска')

# Сохранение логов в БД (успех/неудача)
log_save_success = Counter('log_save_success_total', 'Успешное сохранение логов')
log_save_failure = Counter('log_save_failure_total', 'Ошибка сохранения логов')

# Статус соединения с MySQL (1 - OK, 0 - ошибка)
mysql_connection_status = Gauge('mysql_connection_status', 'Статус соединения с MySQL')

# Для дашборда "Доступность"
security_up = Gauge('security_up', 'Статус доступности сервиса (1 - OK, 0 - DOWN)')

# Для отслеживания ложных срабатываний 
false_positive = Counter('security_false_positive_total', 'Ложные срабатывания')

#начальное значение
security_up.set(1)

# черный список доменов
BLACKLIST_DOMAINS = [
    "malicious.com",
    "spamlink.ru",
    "badad.net",
    "phish.xyz",
    "danger.org",
]
# шаблоны подозрительных конструкций
SUSPICIOUS_PATTERNS = [
    r"<script.*?>.*?</script>",
    r"eval\s*\(",
    r"document\.cookie",
    r"\.exe",
    r"cmd\.exe",
    r"powershell",
    r"wscript\.shell",
    r"onerror\s*=",
    r"onload\s*=",
]
# сервисы коротких ссылок
SHORT_LINK_SERVICES = [
    "bit.ly",
    "tinyurl.com",
    "goo.gl",
    "clck.ru",
    "ow.ly",
]
# хранилище логов в памяти
logs = []

def update_metrics(decision, duration_ms): #Обновление метрик качества
    total_requests.inc()
    analysis_duration.observe(duration_ms)
    if decision == "BLOCKED":
        blocked_by_blacklist.inc()  

def check_url(url): #проверка URL по черному списку и списку коротких ссылок
    if not url:
        return True, None
    for domain in BLACKLIST_DOMAINS:
        if domain in url.lower():
            return False, f"Домен {domain} в черном списке"
    for short in SHORT_LINK_SERVICES:
        if short in url.lower():
            return False, f"Короткие ссылки ({short}) блокируются"
    return True, None

def check_content(text): #проверка контента на наличие подозрительных паттернов
    if not text:
        return True, None
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, f"Обнаружен запрещенный паттерн: {pattern}"
    return True, None

def add_log(url, content, decision, reason, user_ip="127.0.0.1"): #добавление записи в журнал событий
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_ip": user_ip,
        "url": url[:80] if url else "",
        "content_preview": (content[:40] + "...") if len(content) > 40 else content,
        "decision": decision,
        "reason": reason,
    }
    logs.append(log_entry)
    return log_entry

def get_logs(count=20): #возвращает последние записи журнала
    return logs[-count:]

def get_stats(): #возвращает статистику разрешенных/заблокированных проверок
    allowed = sum(1 for log in logs if log["decision"] == "ALLOWED")
    blocked = sum(1 for log in logs if log["decision"] == "BLOCKED")
    return {"allowed": allowed, "blocked": blocked}