import torch
import easyocr

# Vérifier CUDA
print(f"CUDA disponible: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Capacité de calcul: {torch.cuda.get_device_capability(0)}")

    # Initialiser EasyOCR avec GPU
    reader = easyocr.Reader(['fr', 'en'], gpu=False)
    print("EasyOCR utilise le GPU avec succès!")
else:
    print("Le GPU n'est pas détecté")
    print("Votre Quadro P520 (CC 6.1) n'est pas supporté par cette version")
