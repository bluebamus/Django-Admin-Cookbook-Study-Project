# Generated by Django 4.1.3 on 2022-11-30 16:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0010_hero_added_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroProxy',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('entities.hero',),
        ),
    ]