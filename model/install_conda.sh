#!/bin/bash

# Télécharger Miniconda
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-py39_23.5.2-0-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh

# Installer Miniconda avec Python 3.9
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
~/miniconda3/bin/conda init bash

# Créer un environnement dédié avec Python 3.9
~/miniconda3/bin/conda create -y -n skin_env python=3.9

# Ajouter l'activation automatique de l'environnement au .bashrc
echo "conda activate skin_env" >> ~/.bashrc

# Afficher un message pour l'utilisateur
echo "========================================================"
echo "Installation de Miniconda avec Python 3.9 terminée."
echo "Un environnement nommé 'skin_env' a été créé."
echo "Pour l'activer manuellement, exécutez: conda activate skin_env"
echo "L'environnement sera activé automatiquement lors de la prochaine connexion."
echo "========================================================"