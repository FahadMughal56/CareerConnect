# Generated by Django 5.1.5 on 2025-02-01 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_company_id_alter_customuser_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='category',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
