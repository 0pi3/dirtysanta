from django.urls import path, re_path
from . import views

#from core.views import default_context

app_name = 'core'

urlpatterns = [
    path('', views.index, name="index"),
    path('game/new/', views.new_game, name="new_game"),
    path('game/<str:code>/', views.active_game, name="active_game"),
    path('game/<str:code>/details', views.game_details, name="game_details"),
]