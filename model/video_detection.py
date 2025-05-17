from inference.core.workflows import InferencePipeline
import cv2
import numpy as np
import base64
from flask import Response
import threading
import time
import io
from PIL import Image

class VideoDetection:
    def __init__(self):
        self.pipeline = None
        self.latest_frame = None
        self.latest_result = None
        self.is_active = False
        self.lock = threading.Lock()
        self.api_key = "8V5TEzrrRuOJWTfF0Inq"
        self.workspace_name = "tets-hzv1l"
        self.workflow_id = "detect-count-and-visualize-2"
    
    def start_detection(self):
        """Démarre la pipeline de détection vidéo en temps réel"""
        if self.is_active:
            return True
            
        self.is_active = True
        
        # Démarrer la pipeline dans un thread séparé
        detection_thread = threading.Thread(target=self._run_pipeline)
        detection_thread.daemon = True
        detection_thread.start()
        
        return True
    
    def stop_detection(self):
        """Arrête la pipeline de détection vidéo"""
        if not self.is_active:
            return True
            
        self.is_active = False
        
        if self.pipeline:
            self.pipeline.stop()
            self.pipeline = None
        
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
    
    def _frame_processor(self, result, video_frame):
        """Traite chaque frame de la vidéo et les résultats de détection"""
        try:
            if result and result.get("output_image"):
                # Récupérer l'image avec les annotations
                output_image = result["output_image"].numpy_image
                
                with self.lock:
                    self.latest_frame = output_image
                    self.latest_result = result
        except Exception as e:
            print(f"Erreur lors du traitement de la frame: {e}")
    
    def _run_pipeline(self):
        """Exécute la pipeline d'inférence Roboflow"""
        try:
            self.pipeline = InferencePipeline.init_with_workflow(
                api_key=self.api_key,
                workspace_name=self.workspace_name,
                workflow_id=self.workflow_id,
                video_reference=0,  # Caméra par défaut
                max_fps=15,
                on_prediction=self._frame_processor
            )
            
            self.pipeline.start()
            self.pipeline.join()  # Attendre que la pipeline se termine
            
        except Exception as e:
            print(f"Erreur dans la pipeline de détection: {e}")
        finally:
            self.is_active = False
    
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
