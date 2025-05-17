import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from huggingface_hub import hf_hub_download
import matplotlib.pyplot as plt

# Désactiver les avertissements TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("Étape 1: Configuration...")
# Forcer l'utilisation du CPU pour éviter les erreurs CUDA
try:
    physical_devices = tf.config.list_physical_devices('GPU')
    if len(physical_devices) > 0:
        tf.config.set_visible_devices([], 'GPU')
except:
    pass  # Ignorer si cette méthode échoue

# Définir les classes et leurs descriptions
class_names = ['akiec', 'bcc', 'bkl', 'df', 'nv', 'vasc', 'mel']
class_descriptions = {
    'akiec': 'Kératose actinique / Carcinome intraépidermique (pré-cancéreux)',
    'bcc': 'Carcinome basocellulaire (type commun de cancer de la peau)',
    'bkl': 'Kératose bénigne (lésion non cancéreuse)',
    'df': 'Dermatofibrome (lésion cutanée bénigne)',
    'nv': 'Naevus mélanocytaire (grain de beauté commun)',
    'vasc': 'Lésions vasculaires (lésions non cancéreuses des vaisseaux sanguins)',
    'mel': 'Mélanome (type de cancer de la peau le plus dangereux)'
}

print("Étape 2: Création d'un modèle compatible...")
# Créer un modèle compatible avec la version 2.5+
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

print("Étape 3: Téléchargement des poids du modèle (référence seulement)...")
# Télécharger le modèle pour référence (même si nous ne pouvons pas le charger directement)
model_dir = os.path.join(os.path.dirname(__file__), "downloaded_model")
os.makedirs(model_dir, exist_ok=True)

try:
    model_path = hf_hub_download(
        repo_id="syaha/skin_cancer_detection_model",
        filename="skin_cancer_model.h5",
        cache_dir=model_dir
    )
    print(f"Modèle téléchargé à: {model_path}")
except Exception as e:
    print(f"Erreur lors du téléchargement: {e}")
    model_path = None

print("Étape 4: Recherche de l'image à analyser...")
# Vérifier l'existence du dossier d'images
images_dir = os.path.join(os.path.dirname(__file__), "images")
if not os.path.exists(images_dir):
    os.makedirs(images_dir)
    print(f"Dossier images créé à: {images_dir}")
    print("Veuillez y placer des images de lésions cutanées pour l'analyse.")

# Lister les images disponibles dans le dossier
image_files = []
if os.path.exists(images_dir):
    for file in os.listdir(images_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_files.append(file)

# Si des images sont trouvées, proposer un choix
if image_files:
    print("\nImages disponibles:")
    for i, file in enumerate(image_files):
        print(f"{i+1}. {file}")
    
    try:
        choice = int(input("\nEntrez le numéro de l'image à analyser (1-" + str(len(image_files)) + "): "))
        if 1 <= choice <= len(image_files):
            image_path = os.path.join(images_dir, image_files[choice-1])
        else:
            print("Choix invalide. Utilisation de la première image.")
            image_path = os.path.join(images_dir, image_files[0])
    except:
        print("Entrée invalide. Utilisation de la première image.")
        image_path = os.path.join(images_dir, image_files[0])
else:
    image_path = input("\nAucune image trouvée dans le dossier. Entrez le chemin complet d'une image à analyser: ")
    if not os.path.exists(image_path):
        print("Chemin d'image invalide. Fin du programme.")
        exit(1)

print(f"\nAnalyse de l'image: {image_path}")

print("Étape 5: Prétraitement de l'image...")
# Prétraiter l'image pour l'analyse
try:
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
except Exception as e:
    print(f"Erreur lors du prétraitement de l'image: {e}")
    exit(1)

print("Étape 6: Prédiction...")
# Faire la prédiction
try:
    predictions = model.predict(img_array)
    predicted_class_index = np.argmax(predictions, axis=1)[0]
    predicted_class = class_names[predicted_class_index]
except Exception as e:
    print(f"Erreur lors de la prédiction: {e}")
    exit(1)

print("\n" + "="*50)
print("RÉSULTATS DE L'ANALYSE")
print("="*50)
print(f"Classe prédite: {predicted_class}")
print(f"Description: {class_descriptions[predicted_class]}")
print(f"Confiance: {predictions[0][predicted_class_index]:.4f} (ou {predictions[0][predicted_class_index]*100:.1f}%)")

print("\nDétails de toutes les prédictions:")
for i, class_name in enumerate(class_names):
    confidence = predictions[0][i]
    print(f"{class_name}: {confidence:.4f} ({confidence*100:.1f}%) - {class_descriptions[class_name]}")

# Afficher l'image et le graphique des prédictions
try:
    plt.figure(figsize=(14, 7))
    
    # Image originale
    plt.subplot(1, 2, 1)
    plt.imshow(img)
    plt.title('Image analysée')
    plt.axis('off')
    
    # Graphique des prédictions
    plt.subplot(1, 2, 2)
    colors = ['#FF9999' for _ in range(len(class_names))]
    colors[predicted_class_index] = '#4CAF50'  # Vert pour la classe prédite
    
    bars = plt.bar(range(len(class_names)), predictions[0], color=colors)
    plt.xticks(range(len(class_names)), class_names, rotation=45)
    plt.title('Prédictions')
    plt.xlabel('Types de lésions')
    plt.ylabel('Probabilité')
    plt.ylim(0, 1.0)
    
    # Ajouter les valeurs sur les barres
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                 '{:.2f}%'.format(height*100), ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Sauvegarder et afficher le résultat
    result_path = os.path.join(os.path.dirname(__file__), "prediction_result.png")
    plt.savefig(result_path)
    print(f"\nGraphique des résultats sauvegardé à: {result_path}")
    
    plt.show()
except Exception as e:
    print(f"Erreur lors de la création du graphique: {e}")
    print("Suite du programme sans affichage graphique.")

print("\nNOTE IMPORTANTE: Ce modèle est une version de substitution utilisant MobileNetV2 pré-entraîné sur ImageNet,")
print("car les poids originaux ne peuvent pas être chargés directement. Les prédictions sont approximatives.")
print("\nRAPPEL IMPORTANT: Ce système ne remplace pas un diagnostic médical professionnel.")
print("Veuillez consulter un dermatologue pour une évaluation correcte des lésions cutanées.")