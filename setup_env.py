import subprocess
import sys
import os

# Chemin de votre projet
project_dir = r"C:\Users\hp\Desktop\hackathon\ScinScan-AI"
# Nom du nouvel environnement
env_name = "skin_env_isolated"
# Chemin complet de l'environnement
env_path = os.path.join(project_dir, env_name)

print(f"Création d'un environnement virtuel isolé dans {env_path}...")

# Suppression de l'environnement s'il existe déjà
if os.path.exists(env_path):
    print(f"Suppression de l'environnement existant {env_name}...")
    subprocess.run(["rmdir", "/s", "/q", env_path], shell=True)

# Création d'un environnement virtuel complètement isolé
subprocess.check_call([sys.executable, "-m", "venv", env_path, "--clear"])

# Chemin vers pip et python dans le nouvel environnement
pip_path = os.path.join(env_path, "Scripts", "pip.exe")
python_path = os.path.join(env_path, "Scripts", "python.exe")

# Mise à jour de pip
print("Mise à jour de pip...")
subprocess.check_call([pip_path, "install", "--upgrade", "pip"])

# Installation des packages dans le bon ordre
packages = [
    "numpy==1.23.5",
    "tensorflow==2.12.0",
    "flask==2.2.3",
    "werkzeug==2.2.3",
    "opencv-python==4.8.0.76",
    "Pillow==9.5.0",
    "matplotlib==3.7.1",
    "huggingface-hub==0.16.4"
]

for package in packages:
    print(f"Installation de {package}...")
    result = subprocess.run([pip_path, "install", package], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"ERREUR lors de l'installation de {package}: {result.stderr}")
        sys.exit(1)

# Vérification de la version de NumPy
print("Vérification de la version de NumPy...")
result = subprocess.run([python_path, "-c", "import numpy; print(numpy.__version__)"], capture_output=True, text=True)
print(f"Version de NumPy installée: {result.stdout.strip()}")

print("\nEnvironnement configuré avec succès!")
print(f"\nPour activer l'environnement, exécutez:")
print(f"{env_path}\\Scripts\\activate")

# Création du fichier detect.py
detect_file_path = os.path.join(project_dir, "model", "detect.py")
print(f"\nCréation d'un fichier detect.py temporaire dans {detect_file_path}...")

detect_code = '''
# Fonction temporaire pour remplacer l'appel à InferenceHTTPClient
def detect(image_path):
    print(f"Analyse factice de l'image: {image_path}")
    # Retourne une structure compatible vide
    return [{"predictions": {"predictions": []}}]
'''

with open(detect_file_path, "w") as f:
    f.write(detect_code)

print("\nTout est prêt! Pour exécuter l'application:")
print(f"1. Activez l'environnement: {env_path}\\Scripts\\activate")
print(f"2. Naviguez vers le dossier model: cd {os.path.join(project_dir, 'model')}")
print("3. Exécutez l'application: python app.py")