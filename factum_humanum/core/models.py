from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import uuid


def validate_work_file(file):
    """Validate uploaded work file type and size"""
    # 100 MB limit
    max_size = 100 * 1024 * 1024
    if file.size > max_size:
        raise models.ValidationError(f"File size must not exceed 100 MB. You uploaded {file.size / (1024*1024):.1f} MB.")
    
    allowed_extensions = [
        'pdf', 'doc', 'docx', 'txt', 'rtf',  # Documents
        'mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac',  # Audio
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp',  # Images
        'mp4', 'mov', 'avi', 'mkv', 'flv', 'webm',  # Video
        'zip', 'rar', '7z',  # Archives
        'psd', 'ai', 'xd', 'figma',  # Design files
    ]
    ext = file.name.split('.')[-1].lower()
    if ext not in allowed_extensions:
        raise models.ValidationError(f"File type '.{ext}' is not allowed. Allowed types: {', '.join(allowed_extensions)}")


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
    work_file = models.FileField(
        upload_to='works/%Y/%m/%d/',
        validators=[validate_work_file],
        null=True,
        blank=True,
        help_text="Upload your creative work (max 100 MB). Allowed types: documents, audio, images, video, archives, design files."
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.title} by {self.creator.name}"
    
    def get_file_icon(self):
        """Return an emoji icon based on file extension"""
        ext = self.work_file.name.split('.')[-1].lower() if self.work_file else ''
        icons = {
            # Documents
            'pdf': '📄', 'doc': '📝', 'docx': '📝', 'txt': '📄', 'rtf': '📄',
            # Audio
            'mp3': '🎵', 'wav': '🎵', 'flac': '🎵', 'ogg': '🎵', 'm4a': '🎵', 'aac': '🎵',
            # Images
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'bmp': '🖼️', 'svg': '🖼️', 'webp': '🖼️',
            # Video
            'mp4': '🎬', 'mov': '🎬', 'avi': '🎬', 'mkv': '🎬', 'flv': '🎬', 'webm': '🎬',
            # Archives
            'zip': '📦', 'rar': '📦', '7z': '📦',
            # Design
            'psd': '🎨', 'ai': '🎨', 'xd': '🎨', 'figma': '🎨',
        }
        return icons.get(ext, '📎')
