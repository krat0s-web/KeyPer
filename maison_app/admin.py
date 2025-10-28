from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Foyer, Utilisateur, Piece, Animal, StatutTache, Tache,
    TacheAssignee, TacheRecurrente, ListeCourses, Aliment,
    ChatMessage, Recompense, Statistique, Tuto, Inventaire,
    UtilisationRessource, Evenement, TacheEvenement, Dispositif,
    ActionDispositif, Depense, Budget, HistoriqueTache,
    SuggestionTache, PreferenceUtilisateur, InteractionIa, Invitation
)

# === UTILISATEUR (personnalisé) ===
@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('email', 'username', 'role', 'id_foyer', 'is_staff')
    list_filter = ('role', 'is_staff')
    search_fields = ('email', 'username')

# === PIÈCE (UNE SEULE FOIS) ===
@admin.register(Piece)
class PieceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'id_foyer')
    list_filter = ('id_foyer',)
    search_fields = ('nom',)

# === AUTRES MODÈLES (enregistrement simple) ===
admin.site.register(Foyer)
admin.site.register(Animal)
admin.site.register(StatutTache)
admin.site.register(Tache)
admin.site.register(TacheAssignee)
admin.site.register(TacheRecurrente)
admin.site.register(ListeCourses)
admin.site.register(Aliment)
admin.site.register(ChatMessage)
admin.site.register(Recompense)
admin.site.register(Statistique)
admin.site.register(Tuto)
admin.site.register(Inventaire)
admin.site.register(UtilisationRessource)
admin.site.register(Evenement)
admin.site.register(TacheEvenement)
admin.site.register(Dispositif)
admin.site.register(ActionDispositif)
admin.site.register(Depense)
admin.site.register(Budget)
admin.site.register(HistoriqueTache)
admin.site.register(SuggestionTache)
admin.site.register(PreferenceUtilisateur)
admin.site.register(InteractionIa)
admin.site.register(Invitation)