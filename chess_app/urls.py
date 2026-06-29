from django.urls import path
from . import views

urlpatterns = [
    path('start-game/', views.start_game, name='start_game'),
    path('make-move/', views.make_move, name='make_move'),
    path('bot-move-easy/', views.make_bot_move_easy, name='make_bot_move_easy'),
]