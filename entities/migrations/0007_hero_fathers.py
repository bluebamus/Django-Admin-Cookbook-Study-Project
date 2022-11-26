# Generated by Django 4.1.3 on 2022-11-26 16:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("entities", "0006_alter_heroacquaintance_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="hero",
            name="fathers",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="children",
                to="entities.hero",
            ),
        ),
    ]
