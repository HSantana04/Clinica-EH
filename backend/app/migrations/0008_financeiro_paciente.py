# Generated by Django 5.1 on 2024-10-11 18:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_pdfupload'),
    ]

    operations = [
        migrations.AddField(
            model_name='financeiro',
            name='paciente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.paciente'),
        ),
    ]
