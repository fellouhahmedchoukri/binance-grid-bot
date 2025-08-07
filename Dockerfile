# Utilise une image légère Python
FROM python:3.11-slim

WORKDIR /app

# Installe les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code
COPY . .

# Expose le port configuré
EXPOSE ${PORT}

# Démarre avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "app:app"]
