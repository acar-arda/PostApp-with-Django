from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='posts/thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            # Orijinal resmi aç, kopya oluştur ve küçült
            img = Image.open(self.image.path)
            img_copy = img.copy()
            img_copy.thumbnail((300, 300))

            # Thumbnail dosya yolu
            base_name = os.path.basename(self.image.name)
            thumb_path = os.path.join(settings.MEDIA_ROOT, 'posts/thumbnails', base_name)

            # Küçültülmüş resmi kaydet
            img_copy.save(thumb_path)

            # Thumbnail alanını güncelle
            self.thumbnail = f'posts/thumbnails/{base_name}'
            super().save(update_fields=['thumbnail'])

    def __str__(self):
        return f"{self.user.username} - {self.content[:30]}"