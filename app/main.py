from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os

# Создаем приложение FastAPI
app = FastAPI(title="Metrics API Gateway", version="1.0")

# Адрес, по которому наш контейнер будет искать Prometheus внутри Docker-сети
PROMETHEUS_URL = "http://prometheus:9090/api/v1/query"

# Описываем структуру запроса, который будет присылать пользователь
class MetricRequest(BaseModel):
    metric: str

# Эндпоинт 1: Проверка работоспособности (Healthcheck)
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "metrics-gateway"}

# Эндпоинт 2: Получение метрик
@app.post("/api/v1/metrics")
def get_metric(request: MetricRequest):
    metric = request.metric.lower()
    
    # Формируем запрос на языке PromQL в зависимости от того, что попросили
    if metric == "cpu":
        query = '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)'
    elif metric == "memory":
        query = '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100'
    else:
        raise HTTPException(status_code=400, detail="Поддерживаются только метрики: cpu, memory")
    
    try:
        # Делаем запрос к внутреннему API Prometheus
        response = requests.get(PROMETHEUS_URL, params={"query": query}, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Если данных нет (например, Prometheus только запустился)
        if not data.get("data", {}).get("result"):
            return {"error": "Нет данных. Подождите 10-15 секунд, пока Prometheus соберет первые метрики."}
        
        # Достаем значение из ответа Prometheus
        value = data["data"]["result"][0]["value"][1]
        
        return {
            "metric": metric, 
            "value": round(float(value), 2), 
            "unit": "%"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при запросе к Prometheus: {str(e)}")