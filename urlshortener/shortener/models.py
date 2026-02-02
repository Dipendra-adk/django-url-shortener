import string
import random
from django.conf import settings
from django.db import models
from django.utils import timezone

BASE62 = string.ascii_letters + string.digits

def generate_short_code(length=6):
    return ''.join(random.choices(BASE62, k=length))

class ShortenedURL(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    original_url = models.URLField()
    short_key = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    clicks = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    def __str__(self):
        return self.short_key 
    
    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at

    