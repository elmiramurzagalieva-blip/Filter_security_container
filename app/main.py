from flask import Flask, request, jsonify, render_template
from filter_logic import check_url, check_content, update_metrics
from db import init_db, save_log, get_logs_from_db, get_stats_from_db
from prometheus_client import generate_latest, REGISTRY, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)
# инициализация БД
time.sleep(10)
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/check', methods=['POST'])
def api_check():
    start_time = time.time()
    
    data = request.json
    url = data.get('url', '')
    content = data.get('content', '')
    
    url_allowed, url_reason = check_url(url)
    if not url_allowed:
        decision, reason = "BLOCKED", url_reason
    else:
        content_allowed, content_reason = check_content(content)
        if not content_allowed:
            decision, reason = "BLOCKED", content_reason
        else:
            decision, reason = "ALLOWED", "Контент безопасен"
    
    # Обновление метрик
    duration_ms = (time.time() - start_time) * 1000
    update_metrics(decision, duration_ms)
    
    save_log(url, content, decision, reason)
    
    return jsonify({"decision": decision, "reason": reason})

@app.route('/api/logs', methods=['GET'])
def api_logs():
    return jsonify(get_logs_from_db())

@app.route('/api/stats', methods=['GET'])
def api_stats():
    return jsonify(get_stats_from_db())

@app.route('/metrics', methods=['GET'])
def metrics():
    """Эндпоинт для Prometheus"""
    return generate_latest(REGISTRY), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/health', methods=['GET'])
def health():
    """Health check для Kubernetes и Prometheus"""
    from filter_logic import security_up
    security_up.set(1)
    return jsonify({"status": "healthy", "service": "security-container"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)