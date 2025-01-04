# Étape 1 : Utiliser une image Python officielle
FROM python:3.9-slim

# Étape 2 : Définir le répertoire de travail
WORKDIR /app

# Étape 3 : Installer les dépendances système requises
RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    libsm6 \
    libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Étape 4 : Copier les fichiers de votre application
COPY . .

# Étape 5 : Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Installer PyTorch et les dépendances YOLO
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir ultralytics

# Ajouter le support WebSocket
RUN pip install --no-cache-dir "uvicorn[standard]" websockets

# Supprimer le cache PyTorch pour éviter les conflits
RUN rm -rf ~/.cache/torch/hub

# Étape 6 : Exposer le port sur lequel l'application sera exécutée
EXPOSE 8000

# Étape 7 : Lancer l'application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
