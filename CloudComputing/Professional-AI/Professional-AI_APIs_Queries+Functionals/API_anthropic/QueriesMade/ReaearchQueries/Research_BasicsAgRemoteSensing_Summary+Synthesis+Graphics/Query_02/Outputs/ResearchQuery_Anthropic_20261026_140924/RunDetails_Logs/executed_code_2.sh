cd /tmp/deliverables && python3 make_infographic.py --dpi 110 -o /tmp/preview.jpeg && python3 -c "
from PIL import Image; im=Image.open('/tmp/preview.jpeg'); print(im.size)
im.resize((im.width//2, im.height//2)).save('/tmp/preview_small.jpeg', quality=70)"