# Generated by Django 4.1.3 on 2022-11-26 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("entities", "0004_alter_heroacquaintance_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="heroacquaintance",
            name="category",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="entities.category",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="heroacquaintance",
            name="name",
            field=models.CharField(default="lim", max_length=100),
        ),
    ]