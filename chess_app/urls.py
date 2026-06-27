from django.urls import path
from . import views

urlpatterns = [
    path('start-game/', views.start_game, name='start_game'),
    path('make-move/', views.make_move, name='make_move'),
]