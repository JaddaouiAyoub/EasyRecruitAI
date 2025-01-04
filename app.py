import io
import base64
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File ,Request
from fastapi.middleware.cors import CORSMiddleware
import speech_recognition as sr
from PIL import Image, UnidentifiedImageError
import numpy as np
import base64
import torch
import ultralytics
print(ultralytics.__version__)

# Load YOLO model (YOLOv5 for this example)
yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # Change the model to suit your needs (yolov5x, yolov5m, etc.)
# Créer une instance FastAPI
app = FastAPI()

# Ajouter la configuration CORS pour permettre l'accès au frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # L'adresse de votre frontend Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gérer les connexions WebSocket pour l'image
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
    # await websocket.accept()  # Accepter la connexion WebSocket
    # try:
    #     while True:
    #         data = await websocket.receive_text()  # Recevoir les données envoyées par le client

    #         if data.startswith("image:"):  # Si l'on reçoit une image (format base64)
    #             try:
    #                 image_data = data[6:]  # Retirer le préfixe 'image:'
    #                 image = base64.b64decode(image_data)  # Décoder l'image en base64
    #                 image = Image.open(io.BytesIO(image))  # Ouvrir l'image
    #                 image_np = np.array(image)  # Convertir en tableau numpy

    #                 # Analyse d'émotion avec DeepFace
    #                 result = DeepFace.analyze(image_np, actions=['emotion'])
    #                 emotion = result[0]['dominant_emotion']
    #                 confidence = result[0]['emotion'][emotion]
                    
    #                 # Envoyer les résultats au client
    #                 await websocket.send_text(f"Emotion détectée: {emotion} avec une confiance de {confidence}%")

    #             except UnidentifiedImageError:
    #                 print("Image non valide reçue.")
    #             except Exception as e:
    #                 # print(f"Erreur lors de l'analyse d'émotion : {e}")
    #                 continue  # Ignorer l'erreur et continuer à écouter
    #         if data.startswith("audio:"):  # Traitement de l'audio
    #                         try:
    #                             audio_data = data[6:]  # Retirer le préfixe 'audio:'
    #                             print(f"[DEBUG] Longueur des données Base64 : {len(audio_data)}")

    #                             # Décoder les données audio en Base64
    #                             audio_bytes = base64.b64decode(audio_data)
    #                             print(f"[DEBUG] Taille des données audio décodées (bytes) : {len(audio_bytes)}")

    #                             # Convertir en fichier BytesIO
    #                             audio_file = io.BytesIO(audio_bytes)
    #                             print("[DEBUG] Données audio converties en fichier BytesIO.")

    #                             # Détection automatique du format audio
    #                             try:
    #                                 # Utiliser pydub pour lire le fichier et détecter le format
    #                                 audio = AudioSegment.from_file(audio_file)  # Essaie de détecter automatiquement le format
    #                                 print("[DEBUG] Fichier audio ouvert avec pydub.")

    #                             except Exception as e:
    #                                 print(f"[ERROR] Erreur lors de la détection du format audio : {e}")
    #                                 await websocket.send_text("Erreur: Impossible de détecter le format de l'audio.")
    #                                 continue
                                
    #                             # Si nous sommes ici, le format a été détecté et l'audio est valide.
    #                             # Sauvegarder temporairement en WAV pour traitement
    #                             with io.BytesIO() as wav_file:
    #                                 audio.export(wav_file, format="wav")
    #                                 wav_file.seek(0)  # Revenir au début du fichier après l'exportation
    #                                 print("[DEBUG] Fichier audio exporté en format WAV.")

    #                                 # Transcription de l'audio
    #                                 recognizer = sr.Recognizer()

    #                                 with sr.AudioFile(wav_file) as source:
    #                                     print("[DEBUG] Fichier audio ouvert avec 'speech_recognition'.")
    #                                     audio = recognizer.record(source)
    #                                     print("[DEBUG] Fichier audio enregistré pour transcription.")

    #                                 transcription = recognizer.recognize_google(audio)
    #                                 print(f"[DEBUG] Transcription réussie : {transcription}")
    #                                 await websocket.send_text(f"Transcription: {transcription}")

    #                         except sr.UnknownValueError:
    #                             print("[ERROR] L'audio n'a pas pu être compris par l'API.")
    #                             await websocket.send_text("Erreur: L'audio n'a pas pu être compris.")
    #                         except sr.RequestError as re:
    #                             print(f"[ERROR] Problème avec l'API de reconnaissance vocale : {re}")
    #                             await websocket.send_text(f"Erreur avec l'API de reconnaissance vocale : {re}")
    #                         except Exception as e:
    #                             print(f"[ERROR] Erreur inattendue : {e}")
    #                             await websocket.send_text(f"Erreur inattendue : {e}")
    # except WebSocketDisconnect:
    #     print("Client déconnecté")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    try:
        while True:
            data = await websocket.receive_text()  # Receive data sent by client

            if data.startswith("image:"):  # If we receive an image (base64 format)
                try:
                    image_data = data[6:]  # Remove 'image:' prefix
                    image = base64.b64decode(image_data)  # Decode base64 image
                    image = Image.open(io.BytesIO(image))  # Open image
                    image_np = np.array(image)  # Convert to numpy array

                    # YOLO Object Detection
                    results = yolo_model(image_np)  # Perform detection
                    detected_labels = results.names  # Get class names (e.g., 'person', 'cell phone')
                    detected_classes = results.xywh[0][:, -1].tolist()  # Detected object classes
                    detected_confidences = results.xywh[0][:, 4].tolist()  # Confidence levels
                    # Print the raw results to understand what the model is detecting
                    # print("Raw YOLO results:", results)

                    # detected_labels = results.names  # Get class names (e.g., 'person', 'cell phone')
                    # detected_classes = results.xywh[0][:, -1].tolist()  # Detected object classes
                    # detected_confidences = results.xywh[0][:, 4].tolist()  # Confidence levels
                    detected_text = []

                    # Check for people and phones in the detected objects
                    person_count = detected_classes.count(0)  # Class '0' is typically 'person'
                    phone_count = detected_classes.count(67)  # Class '67' is typically 'cell phone'

                    if person_count > 1:
                        detected_text.append(f"Multiple people detected ({person_count} persons)")
                    if phone_count > 0:
                        detected_text.append(f"Phone detected ({phone_count} phone(s))")

                    if detected_text:
                        await websocket.send_text(f"Detection: {', '.join(detected_text)}")
                    else:
                        # print(f"No significant objects detected.")
                        await websocket.send_text("No significant objects detected.")

                except Exception as e:
                    print(f"Error while processing image: {e}")
                    continue  # Ignore error and continue listening
            else:
                continue  # If it's not an image, continue listening

    except WebSocketDisconnect:
        print("Client disconnected")


# Gérer la réception de l'audio via HTTP pour la transcription
@app.post("/transcribe_audio/")
async def transcribe_audio(file: UploadFile = File(...)):
    recognizer = sr.Recognizer()

    # Sauvegarder temporairement l'audio
    audio_data = await file.read()
    audio_file = io.BytesIO(audio_data)

    try:
        # Vérifier si le fichier audio est lisible
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)

        # Utiliser Google Web Speech API pour la transcription
        transcription = recognizer.recognize_google(audio)
        return {"transcription": transcription}

    except ValueError as ve:
        return {"error": "Le fichier audio n'est pas dans un format pris en charge (PCM WAV, AIFF/AIFF-C, FLAC)."}
    except sr.UnknownValueError:
        return {"error": "L'audio n'a pas pu être compris."}
    except sr.RequestError as re:
        return {"error": f"Erreur avec l'API de reconnaissance vocale : {re}"}
    except Exception as e:
        return {"error": f"Une erreur inattendue est survenue : {e}"}




