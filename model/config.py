"""
Configuration du projet SkinScan-AI
"""

import os

# Dossier racine du projet
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Dossiers de l'application
TEMPLATES_DIR = os.path.join(ROOT_DIR, 'templates')
STATIC_DIR = os.path.join(ROOT_DIR, 'static')
UPLOADS_DIR = os.path.join(ROOT_DIR, 'uploads')
PARENT_UPLOADS_DIR = os.path.join(os.path.dirname(ROOT_DIR), 'uploads')
RESOURCES_DIR = os.path.join(ROOT_DIR, 'ressources')
CACHE_DIR = os.path.join(ROOT_DIR, 'cache')
MODEL_DIR = os.path.join(ROOT_DIR, 'downloaded_model')

# Création des dossiers s'ils n'existent pas
for directory in [TEMPLATES_DIR, STATIC_DIR, UPLOADS_DIR, RESOURCES_DIR, CACHE_DIR, MODEL_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configuration de l'API OpenAI
OPENAI_API_KEY = "votre_clef_api_openai"  # À remplacer par votre clé API

# Configuration du modèle de détection de cancer
HF_MODEL_REPO = "syaha/skin_cancer_detection_model"
HF_MODEL_FILENAME = "skin_cancer_model.h5"

# Configuration du modèle RAG pour le chatbot
TRANSFORMERS_MODEL = "Sahajtomar/french_semantic"
DERMATOLOGY_PDF_PATH = os.path.join(RESOURCES_DIR, 'dermatologie_info.pdf')
DERMATOLOGY_TXT_PATH = os.path.join(RESOURCES_DIR, 'dermatologie_info.txt')

# Types de fichiers autorisés
ALLOWED_FILE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 Mo

# Informations sur les classes de lésions
CLASS_NAMES = ['akiec', 'bcc', 'bkl', 'df', 'nv', 'vasc', 'mel']
CLASS_FULL_NAMES = {
    'akiec': 'Kératose actinique / Carcinome intraépidermique',
    'bcc': 'Carcinome basocellulaire',
    'bkl': 'Kératose bénigne',
    'df': 'Dermatofibrome',
    'nv': 'Naevus mélanocytaire',
    'vasc': 'Lésion vasculaire',
    'mel': 'Mélanome'
}

# Descriptions des classes
CLASS_DESCRIPTIONS = {
    'akiec': 'Lésion pré-cancéreuse qui se développe suite à une exposition prolongée au soleil. Peut évoluer en carcinome épidermoïde invasif.',
    'bcc': 'Type de cancer de la peau le plus courant. Se développe lentement et envahit rarement les tissus environnants.',
    'bkl': 'Excroissance bénigne ressemblant à une tache rugueuse et squameuse. Non cancéreuse mais peut être confondue avec d\'autres lésions.',
    'df': 'Nodule cutané bénin ferme et indolore. Généralement inoffensif et ne nécessite pas de traitement si asymptomatique.',
    'nv': 'Communément appelé grain de beauté. La plupart sont bénins, mais certains peuvent évoluer en mélanome.',
    'vasc': 'Anomalies des vaisseaux sanguins cutanés comme les hémangiomes ou les angiomes stellaires. Généralement bénignes.',
    'mel': 'Forme la plus dangereuse de cancer de la peau. Se développe à partir des mélanocytes et peut se propager rapidement à d\'autres parties du corps.'
}

# Niveaux de risque
CLASS_RISKS = {
    'akiec': 'Modéré (pré-cancéreux)',
    'bcc': 'Modéré à élevé',
    'bkl': 'Faible',
    'df': 'Très faible',
    'nv': 'Très faible',
    'vasc': 'Très faible',
    'mel': 'Très élevé'
}

# Recommandations
CLASS_RECOMMENDATIONS = {
    'akiec': 'Consultez un dermatologue dans les 2-4 semaines pour évaluation et traitement.',
    'bcc': 'Consultation dermatologique recommandée dans les 1-2 semaines.',
    'bkl': 'Surveillance régulière. Montrez cette lésion lors de votre prochain contrôle dermatologique.',
    'df': 'Surveillance simple. Généralement inoffensif, mais consultez si des changements apparaissent.',
    'nv': 'Surveillance régulière. Appliquez la règle ABCDE pour détecter tout changement suspect.',
    'vasc': 'Généralement pas préoccupant. Consultez si la lésion saigne, grandit ou change d\'apparence.',
    'mel': 'URGENT: Consultez un dermatologue immédiatement (24-48h). Le mélanome nécessite une prise en charge rapide.'
}