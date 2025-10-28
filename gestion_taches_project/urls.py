from django.contrib import admin
from django.urls import path, include
from maison_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('taches/', views.liste_taches, name='liste_taches'),
    path('foyers/', views.liste_foyers, name='liste_foyers'),
    path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('creer-foyer/', views.creer_foyer, name='creer_foyer'),
    path('ajouter-tache/', views.ajouter_tache, name='ajouter_tache'),
    path('foyer/<int:foyer_id>/inviter/', views.generer_invitation, name='generer_invitation'),  # ← AJOUTÉ
    path('rejoindre/', views.rejoindre_foyer, name='rejoindre_foyer'),
    path('accounts/login/', views.custom_login, name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('tache/<int:tache_id>/supprimer/', views.supprimer_tache, name='supprimer_tache'),
    path('ajouter-piece/', views.ajouter_piece, name='ajouter_piece'),
    path('foyer/<int:foyer_id>/supprimer/', views.supprimer_foyer, name='supprimer_foyer'),

]