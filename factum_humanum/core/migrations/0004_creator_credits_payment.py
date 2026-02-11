from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_work_reviewed_at_work_reviewer_notes_work_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='creator',
            name='credits',
            field=models.IntegerField(default=0, help_text='Number of work registrations available'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(help_text='Email of the purchaser', max_length=254)),
                ('stripe_charge_id', models.CharField(help_text='Stripe charge/session ID', max_length=255, unique=True)),
                ('stripe_session_id', models.CharField(blank=True, max_length=255, unique=True)),
                ('amount_cents', models.IntegerField(help_text='Amount in pence (GBP)')),
                ('currency', models.CharField(default='GBP', max_length=3)),
                ('credits_granted', models.IntegerField(default=5, help_text='Number of credits given for this payment')),
                ('fulfilled', models.BooleanField(default=False, help_text='Whether credits have been added to creator')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('fulfilled_at', models.DateTimeField(blank=True, null=True)),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='core.creator')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
