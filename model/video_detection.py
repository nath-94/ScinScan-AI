import cv2
import numpy as np
from flask import Response
import threading
import time
import io
import os
import tempfile
from detect import detect
from PIL import Image

class VideoDetection:
    def __init__(self):
        self.cap = None
        self.latest_frame = None
        self.latest_result = None
        self.is_active = False
        self.detection_thread = None
        self.lock = threading.Lock()
    
    def start_detection(self):
        """Démarre la détection vidéo en temps réel avec YOLO"""
        if self.is_active:
            return True
            
        self.is_active = True
        
        # Initialiser la caméra
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Erreur: Impossible d'ouvrir la caméra")
            self.is_active = False
            return False
            
        # Démarrer la détection dans un thread séparé
        self.detection_thread = threading.Thread(target=self._run_detection)
        self.detection_thread.daemon = True
        self.detection_thread.start()
        
        return True
    
    def stop_detection(self):
        """Arrête la détection vidéo"""
        if not self.is_active:
            return True
            
        self.is_active = False
        
        # Libérer les ressources de la caméra
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        
        return True
    
    def get_latest_frame(self):
        """Retourne la dernière frame traitée avec les détections"""
        if self.latest_frame is None:
            # Retourner une image noire si aucune frame n'est disponible
            black_image = np.zeros((360, 480, 3), dtype=np.uint8)
            # Ajouter un texte indiquant que la détection est en cours d'initialisation
            cv2.putText(black_image, "Initialisation...", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            _, buffer = cv2.imencode('.jpg', black_image)
            return buffer.tobytes()
        
        with self.lock:
            # Compresser l'image en JPEG
            _, buffer = cv2.imencode('.jpg', self.latest_frame)
            return buffer.tobytes()
    
    def _process_frame_with_detections(self, frame, detections):
        """Ajoute les détections sur l'image"""
        if detections:
            for detection_group in detections:
                predictions = detection_group.get('predictions', {}).get('predictions', [])
                for pred in predictions:
                    # Extraire les coordonnées et dimensions de la boîte englobante
                    x = int(pred.get('x', 0))
                    y = int(pred.get('y', 0))
                    w = int(pred.get('width', 0))
                    h = int(pred.get('height', 0))
                    confidence = pred.get('confidence', 0)
                    class_name = pred.get('class', 'mole')
                    
                    # Dessiner la boîte englobante
                    x1 = int(x - w/2)
                    y1 = int(y - h/2)
                    x2 = int(x + w/2)
                    y2 = int(y + h/2)
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Ajouter le texte avec la classe et la confiance
                    label = f"{class_name}: {confidence:.2f}"
                    cv2.putText(frame, label, (x1, y1-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
    
    def _run_detection(self):
        """Exécute la détection YOLO sur les frames vidéo"""
        try:
            # Importer YOLO directement pour travailler avec des frames en mémoire
            from ultralytics import YOLO
            import os
            
            # Charger le modèle une seule fois
            model_path = os.path.join(os.path.dirname(__file__), "best.pt")
            print(f"Chargement du modèle YOLO depuis: {model_path}")
            model = YOLO(model_path)
            
            while self.is_active and self.cap and self.cap.isOpened():
                # Lire une frame de la caméra
                ret, frame = self.cap.read()
                if not ret:
                    print("Erreur lors de la lecture d'une frame")
                    break
                
                # Appliquer la détection YOLO directement sur la frame en mémoire
                yolo_results = model(frame)
                
                # Convertir les résultats YOLO en format compatible
                class_names = ["mole"]
                image_height, image_width = frame.shape[:2]
                
                from detect import formater_resultats_yolo
                results = [formater_resultats_yolo(yolo_results, image_width, image_height, class_names)]
                
                # Dessiner les détections sur la frame
                frame_with_detections = self._process_frame_with_detections(frame.copy(), results)
                
                # Mettre à jour la dernière frame et les résultats
                with self.lock:
                    self.latest_frame = frame_with_detections
                    self.latest_result = results
                
                # Limiter le taux de rafraîchissement pour économiser les ressources
                time.sleep(0.05)
            
        except Exception as e:
            print(f"Erreur dans la boucle de détection vidéo: {e}")
        finally:
            self.is_active = False
            if self.cap and self.cap.isOpened():
                self.cap.release()
            # Nous n'utilisons plus de répertoire temporaire dans cette version
            pass
    
    def generate_frames(self):
        """Générateur pour le streaming des frames"""
        while True:
            if not self.is_active:
                black_image = np.zeros((360, 480, 3), dtype=np.uint8)
                # Ajouter un texte indiquant que la détection est désactivée
                cv2.putText(black_image, "Detection desactivee", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                _, buffer = cv2.imencode('.jpg', black_image)
                frame = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(0.5)  # Attente avant de générer une nouvelle frame noire
                continue
                
            # Récupérer la frame actuelle
            frame = self.get_latest_frame()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            # Petite pause pour éviter une charge CPU trop importante
            time.sleep(0.05)

# Instance singleton pour le partage entre les routes
video_detector = VideoDetection()
