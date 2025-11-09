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
    path('tache/<int:tache_id>/supprimer/', views.supprimer_tache, name='supprimer_tache'),
    path('ajouter-piece/', views.ajouter_piece, name='ajouter_piece'),
    path('foyer/<int:foyer_id>/supprimer/', views.supprimer_foyer, name='supprimer_foyer'),
    path('ajouter-animal/', views.ajouter_animal, name='ajouter_animal'),
    path('invitation/<int:foyer_id>/', views.generer_invitation, name='generer_invitation'),
    path('logout/', views.custom_logout, name='logout'),
    path('utilisateurs-par-foyer/', views.liste_utilisateurs_par_foyer, name='liste_utilisateurs_par_foyer'),
    path('foyer/<int:foyer_id>/', views.detail_foyer, name='detail_foyer'),
    path('supprimer-membre/<int:user_id>/', views.supprimer_membre, name='supprimer_membre'),
    path('terminer-tache/<int:tache_id>/', views.terminer_tache, name='terminer_tache'),
    path('inscription/', views.inscription, name='inscription'),
]