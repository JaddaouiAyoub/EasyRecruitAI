# Utiliser une image Python alpine plus légère (en fonction des besoins)
FROM python:3.10-alpine

# Installer les dépendances système nécessaires
RUN apk update && apk add --no-cache \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'ensemble du code de l'application
COPY . .

# Exposer le port pour l'API FastAPI
EXPOSE 8000

# Lancer le serveur FastAPI avec Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
