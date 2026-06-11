import easyocr

reader = easyocr.Reader(['fr', 'en'], gpu=True)
result = reader.readtext("webp.jpg")
texte = " ".join([detection[1] for detection in result])

print(texte)