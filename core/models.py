from enum import unique
from typing import cast
from django.conf import settings
from django.db import models


# Create your models here.

class GameSession(models.Model):
    name = models.CharField("Friendly Name", max_length=50)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    complete = models.BooleanField("Game Complete", default=False)
    created_date = models.DateTimeField(auto_now_add=True)

class GamePlayer(models.Model):
    session_id = models.ForeignKey("core.GameSession", verbose_name="Session ID", on_delete=models.CASCADE)
    name = models.CharField("Player Name", max_length=50)
    turn = models.SmallIntegerField("Players Turn Number", blank=True, null=True, default=None)
    possession = models.BooleanField("Player has gift", default=False)

