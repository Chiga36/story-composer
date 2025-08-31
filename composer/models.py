from django.db import models
from django.contrib.auth.models import User

class Background(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    generated_image_url = models.CharField(max_length=500, blank=True, null=True)  # Changed to CharField
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return self.generated_image_url

class Character(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='characters/', blank=True, null=True)
    generated_image_url = models.CharField(max_length=500, blank=True, null=True)  # Changed to CharField
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return self.generated_image_url

class Scene(models.Model):
    POSITION_CHOICES = [
        ('left', 'Left'),
        ('right', 'Right'),
        ('center', 'Center'),
    ]
    
    title = models.CharField(max_length=200)
    background = models.ForeignKey(Background, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    character_position = models.CharField(max_length=10, choices=POSITION_CHOICES)
    action_description = models.TextField()
    generated_image_url = models.CharField(max_length=500, blank=True, null=True)  # Changed to CharField
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
