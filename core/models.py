from enum import unique
from typing import cast
from django.conf import settings
from django.db import models
import uuid

# Create your models here.

class GameSession(models.Model):
    code = models.CharField("Game Code", max_length=6, default=uuid.uuid4().hex[:6].upper(), unique=True, editable=False)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    setup = models.BooleanField("Game Setup & Ready", default=False)
    ready = models.BooleanField("Ready To Start", default=False)
    current_turn = models.IntegerField("Current Players Turn", default=1)
    theif = models.ForeignKey("core.GamePlayer", verbose_name="Previous Theif", on_delete=models.CASCADE, default=None, blank=True, null=True)
    complete = models.BooleanField("Game Complete", default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

class GamePlayer(models.Model):
    session_id = models.ForeignKey("core.GameSession", verbose_name="Session ID", on_delete=models.CASCADE)
    name = models.CharField("Player Name", max_length=50)
    turn = models.SmallIntegerField("Players Turn Number", blank=True, null=True, default=None)
    possession = models.BooleanField("Player has gift", default=False)

    def __str__(self):
        return self.name
