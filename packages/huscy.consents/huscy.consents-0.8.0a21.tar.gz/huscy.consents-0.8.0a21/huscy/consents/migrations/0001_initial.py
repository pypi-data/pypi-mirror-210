from django.db import migrations, models
import django.db.models.deletion
import huscy.consents.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Consent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_fragments', models.JSONField()),
                ('version', models.PositiveIntegerField(default=1)),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ConsentCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('template_text_fragments', models.JSONField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ConsentFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consent_version', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('filehandle', models.FileField(upload_to=huscy.consents.models.get_consent_file_upload_path)),
                ('consent', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='consents.consent')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
