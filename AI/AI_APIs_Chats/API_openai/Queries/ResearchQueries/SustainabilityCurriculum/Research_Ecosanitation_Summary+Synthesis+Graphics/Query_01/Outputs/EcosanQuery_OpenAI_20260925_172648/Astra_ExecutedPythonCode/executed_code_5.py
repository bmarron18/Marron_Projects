from PIL import Image
display(Image.open("/mnt/data/ecosan_concept.png").resize((1000,753)))
display(Image.frombytes("RGB", [d[3].get_pixmap().width,d[3].get_pixmap().height], d[3].get_pixmap().samples))
