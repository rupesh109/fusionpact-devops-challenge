from fastapi import FastAPI
from prometheus_client import Counter, generate_latest
from fastapi.responses import PlainTextResponse

app = FastAPI()
requests_total = Counter('http_requests_total', 'Total HTTP requests')

@app.get("/")
def home():
    requests_total.inc()
    return {"message": "Hello Rupesh!"}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return generate_latest()

