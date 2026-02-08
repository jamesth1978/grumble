from django.db import models
from django.utils import timezone
import uuid


class Creator(models.Model):
    """Stores information about the creator of a work"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Work(models.Model):
    """Stores registered creative works"""
    CATEGORY_CHOICES = [
        ('music', 'Music'),
        ('writing', 'Written Word'),
        ('visual', 'Visual Art'),
        ('film', 'Film/Video'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name='works')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    creation_date = models.DateField(help_text="Date the work was created")
    registered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.title} by {self.creator.name}"
