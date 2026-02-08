# Generated migration file

from django.db import migrations, models
import factum_humanum.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='work_file',
            field=models.FileField(
                blank=True,
                help_text='Upload your creative work (max 100 MB). Allowed types: documents, audio, images, video, archives, design files.',
                null=True,
                upload_to='works/%Y/%m/%d/',
                validators=[factum_humanum.core.models.validate_work_file]
            ),
        ),
    ]
