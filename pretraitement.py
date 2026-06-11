import cv2

# 1. Charger l'image
image = cv2.imread("OIP.webp")

# 2. Niveaux de gris
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 3. Seuillage (noir et blanc)
seuillage = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

# 4. Débruitage
nettoye = cv2.medianBlur(seuillage, 3)

# 5. Sauvegarder l'image prétraitée
cv2.imwrite("webp.jpg", nettoye)

print("Prétraitement terminé")