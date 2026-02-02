import string
import random
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

BASE62 = string.ascii_letters + string.digits

def generate_short_key(length=6):
    return ''.join(random.choices(BASE62, k=length))

def generate_qr_code(url):
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")                                                                                                                                                                                                                                                                                                                                   
    return ContentFile(buffer.getvalue(), name="qr_code.png")