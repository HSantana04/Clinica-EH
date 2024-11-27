# Generated by Django 5.1 on 2024-09-19 15:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_rename_dente1_odontograma_desenho_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='odontograma',
            name='data_atualizacao',
        ),
        migrations.RemoveField(
            model_name='odontograma',
            name='desenho',
        ),
        migrations.AddField(
            model_name='odontograma',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='odontogramas/'),
        ),
        migrations.AlterField(
            model_name='odontograma',
            name='paciente',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.paciente'),
        ),
    ]
