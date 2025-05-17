import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from huggingface_hub import hf_hub_download
import matplotlib
# Importer les nouvelles fonctions de traitement d'image
import cv2
from PIL import Image as PILImage
matplotlib.use('Agg')  # Utiliser le backend Agg pour matplotlib
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import io
import base64
import json

from detect import detect  # Importer la fonction detect

# Configuration de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_clef_secrete_complexe'

# Chemins des dossiers d'uploads (local et parent)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['PARENT_UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16 Mo
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Créer les dossiers nécessaires
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PARENT_UPLOAD_FOLDER'], exist_ok=True)

# Désactiver les avertissements TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Fonction pour vérifier l'extension de fichier
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Définir les classes et leurs descriptions
class_names = ['akiec', 'bcc', 'bkl', 'df', 'nv', 'vasc', 'mel']
class_full_names = {
    'akiec': 'Kératose actinique / Carcinome intraépidermique',
    'bcc': 'Carcinome basocellulaire',
    'bkl': 'Kératose bénigne',
    'df': 'Dermatofibrome',
    'nv': 'Naevus mélanocytaire',
    'vasc': 'Lésion vasculaire',
    'mel': 'Mélanome'
}

class_descriptions = {
    'akiec': 'Lésion pré-cancéreuse qui se développe suite à une exposition prolongée au soleil. Peut évoluer en carcinome épidermoïde invasif.',
    'bcc': 'Type de cancer de la peau le plus courant. Se développe lentement et envahit rarement les tissus environnants.',
    'bkl': 'Excroissance bénigne ressemblant à une tache rugueuse et squameuse. Non cancéreuse mais peut être confondue avec d\'autres lésions.',
    'df': 'Nodule cutané bénin ferme et indolore. Généralement inoffensif et ne nécessite pas de traitement si asymptomatique.',
    'nv': 'Communément appelé grain de beauté. La plupart sont bénins, mais certains peuvent évoluer en mélanome.',
    'vasc': 'Anomalies des vaisseaux sanguins cutanés comme les hémangiomes ou les angiomes stellaires. Généralement bénignes.',
    'mel': 'Forme la plus dangereuse de cancer de la peau. Se développe à partir des mélanocytes et peut se propager rapidement à d\'autres parties du corps.'
}

class_risks = {
    'akiec': 'Modéré (pré-cancéreux)',
    'bcc': 'Modéré à élevé',
    'bkl': 'Faible',
    'df': 'Très faible',
    'nv': 'Très faible',
    'vasc': 'Très faible',
    'mel': 'Très élevé'
}

class_recommendations = {
    'akiec': 'Consultez un dermatologue dans les 2-4 semaines pour évaluation et traitement.',
    'bcc': 'Consultation dermatologique recommandée dans les 1-2 semaines.',
    'bkl': 'Surveillance régulière. Montrez cette lésion lors de votre prochain contrôle dermatologique.',
    'df': 'Surveillance simple. Généralement inoffensif, mais consultez si des changements apparaissent.',
    'nv': 'Surveillance régulière. Appliquez la règle ABCDE pour détecter tout changement suspect.',
    'vasc': 'Généralement pas préoccupant. Consultez si la lésion saigne, grandit ou change d\'apparence.',
    'mel': 'URGENT: Consultez un dermatologue immédiatement (24-48h). Le mélanome nécessite une prise en charge rapide.'
}

# Création du modèle et téléchargement des poids
print("Initialisation du modèle...")
# Forcer l'utilisation du CPU
try:
    physical_devices = tf.config.list_physical_devices('GPU')
    if len(physical_devices) > 0:
        tf.config.set_visible_devices([], 'GPU')
except:
    pass

def create_model():
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False
    
    model = tf.keras.Sequential([
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(7, activation='softmax')
    ])
    return model

model = create_model()
print("Modèle créé avec succès")

# Télécharger le modèle pour référence
try:
    model_dir = os.path.join(os.path.dirname(__file__), "downloaded_model")
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = hf_hub_download(
        repo_id="syaha/skin_cancer_detection_model",
        filename="skin_cancer_model.h5",
        cache_dir=model_dir
    )
    print(f"Modèle de référence téléchargé à: {model_path}")
except Exception as e:
    print(f"Note: {e}")

# Fonction de prédiction
def predict_image(img_path):
    try:
        img = PILImage.open(img_path).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        predictions = model.predict(img_array)
        predicted_class_index = np.argmax(predictions, axis=1)[0]
        predicted_class = class_names[predicted_class_index]
        
        # Créer le graphique
        plt.figure(figsize=(10, 6))
        
        # Palette de couleurs moderne
        colors = ['#e9ecef' for _ in range(len(class_names))]
        colors[predicted_class_index] = '#4361ee'  # Bleu vif pour la classe prédite
        
        # Créer le graphique avec style
        bars = plt.bar(range(len(class_names)), predictions[0], color=colors, edgecolor='white', linewidth=1)
        plt.xticks(range(len(class_names)), class_names, rotation=45, fontsize=12)
        plt.title('Prédictions par type de lésion', fontsize=14, pad=20)
        plt.xlabel('Types de lésions', fontsize=12, labelpad=10)
        plt.ylabel('Probabilité', fontsize=12, labelpad=10)
        plt.ylim(0, 1.0)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                     '{:.1f}%'.format(height*100), ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        # Customiser l'apparence
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
        
        # Convertir le graphique en image base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        graph_img = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        # Préparer les données pour le JavaScript
        chart_data = {
            'labels': class_names,
            'values': [float(p) for p in predictions[0]],
            'predicted_index': int(predicted_class_index)
        }
        
        predicted_risk = class_risks[predicted_class]
        
        return {
            'success': True,
            'class_name': predicted_class,
            'class_full_name': class_full_names[predicted_class],
            'class_description': class_descriptions[predicted_class],
            'class_risk': predicted_risk,
            'has_high_risk': is_high_risk(predicted_risk),
            'recommendation': class_recommendations[predicted_class],
            'confidence': float(predictions[0][predicted_class_index]),
            'graph_img': graph_img,
            'chart_data': chart_data,
            'predictions': {class_names[i]: float(predictions[0][i]) for i in range(len(class_names))}
        }
    except Exception as e:
        print(f"Erreur lors de la prédiction: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# Fonction pour traiter les grains de beauté détectés
def process_detected_moles(img_path):
    try:
        # Utiliser la fonction detect pour obtenir les grains de beauté
        detection_results = detect(img_path)
        
        # Adapter le format de résultat retourné par la fonction detect()
        # La fonction detect() retourne une liste avec un dictionnaire
        if isinstance(detection_results, list) and len(detection_results) > 0:
            detection_result = detection_results[0]
            if 'predictions' in detection_result and 'predictions' in detection_result['predictions']:
                predictions = detection_result['predictions']['predictions']
            else:
                print("Format de résultat inattendu: les prédictions sont introuvables.")
                return predict_image(img_path)
        else:
            print("Aucun grain de beauté détecté dans l'image.")
            return predict_image(img_path)
        
        # Vérifier si des objets ont été détectés
        if not predictions or len(predictions) == 0:
            print("Aucun grain de beauté détecté dans l'image.")
            # Si aucun grain de beauté n'est détecté, utiliser l'image entière
            return predict_image(img_path)
        
        # Lire l'image originale
        original_img = cv2.imread(img_path)
        if original_img is None:
            print(f"Impossible de lire l'image: {img_path}")
            return predict_image(img_path)
        
        original_img_rgb = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
        
        # Liste pour stocker les résultats de chaque grain de beauté
        mole_results = []
        
        # Pour chaque grain de beauté détecté
        for i, prediction in enumerate(predictions):
            # Extraire les coordonnées de la boîte englobante
            x = prediction['x']
            y = prediction['y']
            width = prediction['width']
            height = prediction['height']
            confidence = prediction.get('confidence', 0)
            
            # Si la confiance est trop faible, ignorer cette détection
            if confidence < 0.5:
                continue
                
            # Afficher les valeurs brutes pour le débogage
            print(f"Grain {i}: x={x}, y={y}, width={width}, height={height}")
            
            # Calculer les coordonnées en pixels - s'assurer qu'ils sont bien normalisés
            img_height, img_width = original_img.shape[:2]
            
            # Vérifier si les coordonnées sont déjà en pixels ou sont normalisées
            if x > 1.0 or y > 1.0:
                # Les coordonnées sont déjà en pixels
                x1 = max(0, int(x - width/2))
                y1 = max(0, int(y - height/2))
                x2 = min(img_width, int(x + width/2))
                y2 = min(img_height, int(y + height/2))
            else:
                # Les coordonnées sont normalisées (entre 0 et 1)
                x1 = max(0, int((x - width/2) * img_width))
                y1 = max(0, int((y - height/2) * img_height))
                x2 = min(img_width, int((x + width/2) * img_width))
                y2 = min(img_height, int((y + height/2) * img_height))
            
            # S'assurer que la région a une taille minimale
            if (x2 - x1) < 10:
                center_x = (x1 + x2) // 2
                x1 = max(0, center_x - 20)
                x2 = min(img_width, center_x + 20)
                
            if (y2 - y1) < 10:
                center_y = (y1 + y2) // 2
                y1 = max(0, center_y - 20)
                y2 = min(img_height, center_y + 20)
            
            # Élargir légèrement la zone pour s'assurer que tout le grain de beauté est inclus
            padding = 20  # Augmenter le padding
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(img_width, x2 + padding)
            y2 = min(img_height, y2 + padding)
            
            # Vérifier que les dimensions sont valides
            print(f"Grain {i}: Coordonnées calculées: x1={x1}, y1={y1}, x2={x2}, y2={y2}, largeur={x2-x1}, hauteur={y2-y1}")
            
            # Extraire le grain de beauté
            mole_img = original_img_rgb[y1:y2, x1:x2]
            
            # Vérifier si l'image extraite est valide (non vide)
            if mole_img.size == 0 or mole_img.shape[0] == 0 or mole_img.shape[1] == 0:
                print(f"Image du grain de beauté {i} invalide, dimensions: {mole_img.shape}")
                continue
            
            # Sauvegarder temporairement l'image du grain de beauté
            mole_filename = f"mole_{i}.jpg"
            mole_path = os.path.join(app.config['UPLOAD_FOLDER'], mole_filename)
            
            # Vérifier à nouveau avant d'appeler cvtColor
            try:
                cv2.imwrite(mole_path, cv2.cvtColor(mole_img, cv2.COLOR_RGB2BGR))
                
                # Analyser le grain de beauté avec le modèle
                mole_result = predict_image(mole_path)
                
                # Ajouter les coordonnées à la réponse
                if mole_result['success']:
                    mole_result['coordinates'] = {
                        'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2
                    }
                    mole_results.append(mole_result)
            except Exception as e:
                print(f"Erreur lors du traitement du grain de beauté {i}: {e}")
                continue
        
        # Si aucun grain de beauté n'a été analysé avec succès, utiliser l'image entière
        if not mole_results:
            result = predict_image(img_path)
            # Ajouter l'indicateur de risque élevé (single mole case)
            result['has_high_risk'] = is_high_risk(result.get('class_risk', ''))
            return result
        
        # Trouver le résultat avec le risque le plus élevé
        highest_risk_result = max(mole_results, key=lambda r: get_risk_score(r['class_risk']))
        
        # Vérifier si un des grains de beauté présente un risque supérieur à modéré
        has_high_risk = any(is_high_risk(result['class_risk']) for result in mole_results)
        
        # Créer une copie modifiable des résultats avec uniquement les données essentielles
        clean_mole_results = []
        for result in mole_results:
            # Créer une copie sans les références circulaires
            clean_result = {
                'class_name': result['class_name'],
                'class_full_name': result['class_full_name'],
                'class_risk': result['class_risk'],
                'confidence': result['confidence'],
                'coordinates': result.get('coordinates', {}),
                'chart_data': result.get('chart_data', {}),  # Ajouter les données de graphique pour chaque grain de beauté
                'class_description': result.get('class_description', ''),  # Ajouter la description
                'recommendation': result.get('recommendation', ''),  # Ajouter la recommandation
                'predictions': result.get('predictions', {})  # Ajouter les prédictions pour toutes les classes
            }
            clean_mole_results.append(clean_result)
        
        # Dessiner les boîtes englobantes sur l'image originale
        _, filename = os.path.split(img_path)
        annotated_filename = f"annotated_{filename}"
        annotated_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
        annotated_image_path = draw_bounding_boxes(img_path, clean_mole_results, annotated_path)
        
        # Ajouter toutes les détections au résultat final
        highest_risk_result['all_detections'] = clean_mole_results
        highest_risk_result['total_moles_detected'] = len(predictions)
        highest_risk_result['analyzed_moles'] = len(mole_results)
        highest_risk_result['has_high_risk'] = has_high_risk
        
        # Utiliser la fonction robuste pour générer l'URL de l'image annotée
        if annotated_image_path:
            highest_risk_result['annotated_image'] = get_image_url(annotated_filename)
            print(f"URL de l'image annotée: {highest_risk_result['annotated_image']}")
        else:
            highest_risk_result['annotated_image'] = None
        
        return highest_risk_result
        
    except Exception as e:
        print(f"Erreur lors du traitement des grains de beauté détectés: {e}")
        # En cas d'erreur, utiliser l'analyse de l'image entière
        return predict_image(img_path)

# Fonction pour attribuer un score numérique au niveau de risque
def get_risk_score(risk_level):
    risk_scores = {
        'Très faible': 1,
        'Faible': 2,
        'Modéré': 3,
        'Modéré (pré-cancéreux)': 3.5,
        'Modéré à élevé': 4,
        'Élevé': 4.5,
        'Très élevé': 5
    }
    return risk_scores.get(risk_level, 1)

# Fonction pour déterminer si un risque est supérieur à modéré
def is_high_risk(risk_level):
    high_risk_levels = ['Modéré à élevé', 'Élevé', 'Très élevé']
    return risk_level in high_risk_levels

# Fonction pour dessiner les boîtes englobantes sur l'image
def draw_bounding_boxes(img_path, detections, save_path=None):
    """
    Dessine les boîtes englobantes sur l'image et numérote les grains de beauté détectés.
    
    Args:
        img_path: Chemin de l'image d'origine
        detections: Liste des détections avec leur coordonnées
        save_path: Chemin pour sauvegarder l'image avec les annotations (si None, utilise un nom par défaut)
    
    Returns:
        Le chemin vers l'image annotée
    """
    print(f"Drawing bounding boxes for image: {img_path}")
    print(f"Save path: {save_path}")
    
    # Lire l'image
    image = cv2.imread(img_path)
    if image is None:
        print(f"Impossible de lire l'image: {img_path}")
        
        # Essayer de lire l'image depuis le dossier parent si elle n'est pas trouvée
        parent_img_path = os.path.join(app.config['PARENT_UPLOAD_FOLDER'], os.path.basename(img_path))
        print(f"Tentative avec le chemin parent: {parent_img_path}")
        image = cv2.imread(parent_img_path)
        
        if image is None:
            print(f"Image introuvable dans les deux emplacements.")
            return None
    
    # Créer une copie pour ne pas modifier l'original
    annotated_img = image.copy()
    
    # Définir les couleurs (BGR)
    box_color = (0, 255, 0)  # Green
    text_color = (255, 255, 255)  # Blanc
    high_risk_box_color = (0, 0, 255)  # Rouge pour les grains à risque élevé
    
    # Pour chaque détection
    for i, detection in enumerate(detections):
        if not detection.get('coordinates'):
            continue
            
        # Récupérer les coordonnées
        x1 = detection['coordinates']['x1']
        y1 = detection['coordinates']['y1']
        x2 = detection['coordinates']['x2']
        y2 = detection['coordinates']['y2']
        
        # Déterminer si c'est un grain de beauté à risque élevé
        is_high_risk = detection.get('class_risk', '').startswith('Élevé') or detection.get('class_risk', '').startswith('Très élevé')
        current_box_color = high_risk_box_color if is_high_risk else box_color
        
        # Dessiner la boîte avec une épaisseur et un style qui dépend du risque
        thickness = 3 if is_high_risk else 2
        cv2.rectangle(annotated_img, (x1, y1), (x2, y2), current_box_color, thickness)
        
        # Créer un cercle plus visible pour le numéro
        circle_radius = 14
        center = (x1 + circle_radius + 4, y1 + circle_radius + 4)
        cv2.circle(annotated_img, center, circle_radius, current_box_color, -1)
        
        # Ajouter un contour blanc au cercle pour le rendre plus visible
        cv2.circle(annotated_img, center, circle_radius, (255, 255, 255), 1)
        
        # Ajouter le numéro avec une taille plus grande
        font_scale = 0.6  # Augmenter la taille de la police
        cv2.putText(
            annotated_img, 
            str(i+1), 
            (center[0] - 5, center[1] + 5),  # Position ajustée
            cv2.FONT_HERSHEY_SIMPLEX, 
            font_scale,
            text_color,  # Couleur
            1,  # Épaisseur
            cv2.LINE_AA  # Type de ligne
        )
    
    # Sauvegarder l'image annotée
    if save_path is None:
        base_path, ext = os.path.splitext(img_path)
        save_path = f"annotated_{base_path}{ext}"
    
    cv2.imwrite(save_path, annotated_img)
    return save_path

# Routes Flask
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Traitement AJAX
        if 'file' not in request.files:
            return json.dumps({'success': False, 'error': 'Aucun fichier sélectionné'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return json.dumps({'success': False, 'error': 'Aucun fichier sélectionné'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Utiliser la détection et l'analyse des grains de beauté
            result = process_detected_moles(filepath)
            
            if result['success']:
                # Utiliser la fonction robuste pour générer les URLs d'images
                result['file_url'] = get_image_url(filename)
                
                # Si une image annotée a été générée, mettre à jour son URL également
                if result.get('annotated_image'):
                    # Récupérer juste le nom du fichier de l'URL
                    annotated_filename = os.path.basename(result['annotated_image'])
                    result['annotated_image'] = get_image_url(annotated_filename)
                
                # Sérialiser en JSON de manière sécurisée pour éviter les références circulaires
                try:
                    return json.dumps(result)
                except ValueError as e:
                    print(f"Erreur de sérialisation JSON: {e}")
                    # Version simplifiée du résultat en cas d'erreur
                    safe_result = {
                        'success': True,
                        'class_name': result['class_name'],
                        'class_full_name': result['class_full_name'],
                        'confidence': result['confidence'],
                        'file_url': result['file_url'],
                        'recommendation': result['recommendation'],
                        'total_moles_detected': result.get('total_moles_detected', 0),
                        'analyzed_moles': result.get('analyzed_moles', 0)
                    }
                    return json.dumps(safe_result)
            else:
                return json.dumps({'success': False, 'error': result['error']}), 500
        else:
            return json.dumps({'success': False, 'error': 'Type de fichier non autorisé. Utilisez JPG, JPEG ou PNG.'}), 400
    
    # GET request - afficher la page
    return render_template('index.html', 
                          class_names=class_names,
                          class_full_names=class_full_names,
                          class_descriptions=class_descriptions)

@app.route('/result')
def result():
    return render_template('result.html')

# Fonction pour créer des URLs d'images robustes
def get_image_url(filename):
    """Génère une URL pour une image en vérifiant d'abord si elle existe."""
    # Vérifier dans le dossier uploads local
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        return url_for('uploaded_file', filename=filename)
    
    # Vérifier dans le dossier uploads parent
    if os.path.exists(os.path.join(app.config['PARENT_UPLOAD_FOLDER'], filename)):
        return url_for('uploaded_file', filename=filename)
    
    # Si le fichier n'existe pas, retourner None
    return None

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Vérifier si le fichier est dans le dossier uploads du projet parent
    if os.path.exists(os.path.join(app.config['PARENT_UPLOAD_FOLDER'], filename)):
        return send_from_directory(app.config['PARENT_UPLOAD_FOLDER'], filename)
    # Sinon, chercher dans le dossier uploads de l'application
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

#if __name__ == '__main__':
 #   app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
