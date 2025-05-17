import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from huggingface_hub import hf_hub_download
import matplotlib
matplotlib.use('Agg')  # Utiliser le backend Agg pour matplotlib
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import io
import base64
import json

# Configuration de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_clef_secrete_complexe'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16 Mo
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Créer les dossiers nécessaires
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0
        
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
        
        return {
            'success': True,
            'class_name': predicted_class,
            'class_full_name': class_full_names[predicted_class],
            'class_description': class_descriptions[predicted_class],
            'class_risk': class_risks[predicted_class],
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
            
            # Faire la prédiction
            result = predict_image(filepath)
            
            if result['success']:
                result['file_url'] = url_for('uploaded_file', filename=filename)
                return json.dumps(result)
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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)