# Generated by Django 5.1 on 2024-10-31 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_remove_financeiro_data_vencimento_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='financeiro',
            name='data_vencimento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='financeiro',
            name='periodo_apuracao',
            field=models.DateField(blank=True, null=True),
        ),
    ]
