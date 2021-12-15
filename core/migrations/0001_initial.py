# Generated by Django 3.2.9 on 2021-12-15 05:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GamePlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Player Name')),
                ('turn', models.SmallIntegerField(blank=True, default=None, null=True, verbose_name='Players Turn Number')),
                ('possession', models.BooleanField(default=False, verbose_name='Player has gift')),
                ('phone', models.BooleanField(default=False, verbose_name='Player using phone')),
            ],
        ),
        migrations.CreateModel(
            name='GameSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default='E71C26', editable=False, max_length=6, unique=True, verbose_name='Game Code')),
                ('setup', models.BooleanField(default=False, verbose_name='Game Setup & Ready')),
                ('ready', models.BooleanField(default=False, verbose_name='Ready To Start')),
                ('current_turn', models.IntegerField(default=1, verbose_name='Current Players Turn')),
                ('complete', models.BooleanField(default=False, verbose_name='Game Complete')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('completion_date', models.DateTimeField(auto_now=True)),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('theif', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.gameplayer', verbose_name='Previous Theif')),
            ],
        ),
        migrations.AddField(
            model_name='gameplayer',
            name='session_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.gamesession', verbose_name='Session ID'),
        ),
    ]
