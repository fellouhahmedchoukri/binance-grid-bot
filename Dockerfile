# Dockerfile

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exposer le port injecté par Railway
ENV PORT 5000
EXPOSE $PORT

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]
