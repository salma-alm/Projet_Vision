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

Placer les images dans `images/raw/`, puis :

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

**Auteurs :** Ataa Ahmadoune & Salma EL ALAMI
**Encadrement :** LACHKAR ABDELMOUNAIM
**Contexte :** Projet académique - Traitement d'images
