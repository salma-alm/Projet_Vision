# Pipeline OCR — Plaques d'immatriculation

Extraction automatique du numéro de plaque à partir de photos de voitures européennes.

## Installation

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# Mac / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

> EasyOCR télécharge ses modèles automatiquement au premier lancement (~100 Mo).

## Utilisation

Placer les images de la [base de données](https://www.kaggle.com/datasets/tielemarvin/european-license-plate-dataset-elpd?select=COCO) dans `images/raw/`, ou votre propre image coupée dans `images/cropped/`, puis :

```bash
python pipeline.py
```

## Structure

```
images/raw/          ← photos d'entrée
images/cropped/      ← généré automatiquement
images/processed/    ← généré automatiquement
annotations/         ← fichier JSON du dataset Kaggle
```

## À propos

**Auteurs :** Atae AHMADOUN & Salma EL ALAMI   
**Encadrement :** Abdelmounaim LACHKAR   
**Contexte :** Projet académique à l'ENSA Tanger - Traitement d'images
