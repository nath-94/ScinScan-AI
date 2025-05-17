import os
import unittest
from app import app, detect, draw_bounding_boxes, process_detected_moles
import io
from PIL import Image
import cv2
import numpy as np

class TestSkinScanAI(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.test_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                          '..', 'uploads', 'grainsdebeaute-858x572.jpg')

    def test_detect_function(self):
        """Test que la fonction de détection retourne un résultat valide"""
        if os.path.exists(self.test_image_path):
            result = detect(self.test_image_path)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, list)
            if len(result) > 0:
                self.assertIsInstance(result[0], dict)
                self.assertIn('predictions', result[0])
        else:
            print(f"Image test introuvable: {self.test_image_path}")

    def test_draw_bounding_boxes(self):
        """Test que la fonction de dessin des boîtes englobantes fonctionne correctement"""
        if os.path.exists(self.test_image_path):
            # Créer des détections fictives
            detections = [
                {'coordinates': {'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200}, 'class_risk': 'Faible'},
                {'coordinates': {'x1': 300, 'y1': 300, 'x2': 400, 'y2': 400}, 'class_risk': 'Très élevé'}
            ]
            
            # Dessiner les boîtes
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test_boxes.jpg')
            result_path = draw_bounding_boxes(self.test_image_path, detections, output_path)
            
            # Vérifier que le fichier a été créé
            self.assertIsNotNone(result_path)
            self.assertTrue(os.path.exists(result_path))
            
            # Nettoyer
            if os.path.exists(output_path):
                os.remove(output_path)
        else:
            print(f"Image test introuvable: {self.test_image_path}")

    def test_process_detected_moles(self):
        """Test que la fonction de traitement des grains de beauté fonctionne correctement"""
        if os.path.exists(self.test_image_path):
            result = process_detected_moles(self.test_image_path)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, dict)
            self.assertTrue(result['success'])
            self.assertIn('class_name', result)
            self.assertIn('confidence', result)
        else:
            print(f"Image test introuvable: {self.test_image_path}")

    def test_index_page(self):
        """Test que la page d'index se charge correctement"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SkinScan-AI', response.data)

if __name__ == '__main__':
    unittest.main()
