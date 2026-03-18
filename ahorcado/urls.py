from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('nuevo/', views.new_game, name='new_game'),
    path('probar/', views.guess_letter, name='guess_letter'),
    path('reiniciar/', views.reset_game, name='reset_game'),
    path('health/', views.health, name='health'),
]
