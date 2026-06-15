# Filter Security Container

Контейнер информационной безопасности для защиты от угрозы внедрения вредоносного кода через рекламу, сервисы и контент (УБИ.186)

## Description

Security Container protects information systems from threat malicious code injection via ads, third‑party services, and user content. It intercepts requests, filters URLs and content, blocks threats, stores audit logs in MySQL, and exports metrics to Prometheus + Grafana.

## Key Features

- Blacklist domain filtering
- Short link blocking (bit.ly, clck.ru, etc.)
- XSS / malicious pattern detection (`<script>`, `eval(`, `.exe`, `powershell`, etc.)
- HTTPS enforcement (HTTP → 301 redirect, client‑side `http://` block)
- Audit logging (MySQL)
- Monitoring (Prometheus + Grafana)
- Docker / Kubernetes deployment

## Tech Stack

Python 3.12 / Flask / Nginx / MySQL / phpMyAdmin / Prometheus / Grafana / Docker / Kubernetes

## License

Academic Free License v. 3.0

## Author

Murzagalieva E.A., KP-23-17, Gubkin University
