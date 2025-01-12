# Utiliser une image Python comme base
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires dans le conteneur
COPY . /app/

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port utilisé par FastAPI
EXPOSE 8000

# Lancer l'application avec uvicorn (serveur ASGI)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
