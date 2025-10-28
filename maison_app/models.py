from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta

# === CHOIX DE RÔLE (AU NIVEAU DU MODULE) ===
ROLE_CHOICES = [
    ('admin', 'Administrateur'),
    ('tresorier', 'Trésorier'),
    ('membre', 'Membre'),
    ('junior', 'Junior'),
    ('invite', 'Invité'),
    ('superviseur', 'Superviseur'),
    ('observateur', 'Observateur'),
]

# === MANAGER PERSONNALISÉ ===
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'utilisateur doit avoir un email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

# === UTILISATEUR ===
class Utilisateur(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='membre')
    id_foyer = models.ForeignKey('Foyer', on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    class Meta:
        db_table = 'utilisateur'

    def __str__(self):
        return self.email

# === FOYER ===
class Foyer(models.Model):
    nom = models.CharField(max_length=100)
    nb_pieces = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'foyer'

    def __str__(self):
        return self.nom

class Piece(models.Model):
    nom = models.CharField(max_length=100)
    id_foyer = models.ForeignKey(
        Foyer, 
        on_delete=models.CASCADE, 
        related_name='pieces'  # ← AJOUTÉ
    )

    class Meta:
        db_table = 'piece'

    def __str__(self):
        return self.nom

# === INVITATION ===
class Invitation(models.Model):
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='membre')
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    utilise = models.BooleanField(default=False)

    def est_valide(self):
        return not self.utilise and self.date_creation >= timezone.now() - timedelta(days=7)

# === ANIMAL ===
class Animal(models.Model):
    nom = models.CharField(max_length=100)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)
    id_piece = models.ForeignKey(Piece, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'animal'

    def __str__(self):
        return self.nom

# === STATUT TÂCHE ===
class StatutTache(models.Model):
    libelle = models.CharField(max_length=50, choices=[
        ('À faire', 'À faire'),
        ('En cours', 'En cours'),
        ('Terminée', 'Terminée'),
        ('Annulée', 'Annulée')
    ])

    class Meta:
        db_table = 'statut_tache'

    def __str__(self):
        return self.libelle

# === TÂCHE ===
class Tache(models.Model):
    titre = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date_limite = models.DateField(null=True, blank=True)
    priorite = models.CharField(max_length=20, choices=[
        ('Haute', 'Haute'),
        ('Moyenne', 'Moyenne'),
        ('Basse', 'Basse')
    ], null=True, blank=True)
    id_statut = models.ForeignKey(StatutTache, on_delete=models.SET_NULL, null=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)
    id_piece = models.ForeignKey(Piece, on_delete=models.SET_NULL, null=True, blank=True)  # ← NOUVEAU

    class Meta:
        db_table = 'tache'

    def __str__(self):
        return self.titre
# === TÂCHE ASSIGNÉE ===
class TacheAssignee(models.Model):
    id_tache = models.ForeignKey(Tache, on_delete=models.CASCADE)
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    id_piece = models.ForeignKey(Piece, on_delete=models.SET_NULL, null=True)
    date_assignation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tache_assignee'
        unique_together = ('id_tache', 'id_user')

    def __str__(self):
        return f"{self.id_tache.titre} - {self.id_user.nom}"

# === TÂCHE RÉCURRENTE ===
class TacheRecurrente(models.Model):
    id_tache = models.ForeignKey(Tache, on_delete=models.CASCADE)
    frequence = models.CharField(max_length=20, choices=[
        ('Quotidien', 'Quotidien'),
        ('Hebdo', 'Hebdo'),
        ('Mensuel', 'Mensuel')
    ])
    dernier_execution = models.DateField(null=True)

    class Meta:
        db_table = 'tache_recurrente'

    def __str__(self):
        return f"{self.id_tache.titre} - {self.frequence}"

# === LISTE DE COURSES ===
class ListeCourses(models.Model):
    nom = models.CharField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)
    statut = models.CharField(max_length=20, choices=[
        ('En cours', 'En cours'),
        ('Acheté', 'Acheté')
    ])

    class Meta:
        db_table = 'liste_courses'

    def __str__(self):
        return self.nom

# === ALIMENT ===
class Aliment(models.Model):
    nom = models.CharField(max_length=100)
    id_liste = models.ForeignKey(ListeCourses, on_delete=models.CASCADE)
    quantite = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    unite = models.CharField(max_length=20, null=True)

    class Meta:
        db_table = 'aliment'

    def __str__(self):
        return self.nom

# === CHAT MESSAGE ===
class ChatMessage(models.Model):
    id_user = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    id_tache = models.ForeignKey(Tache, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'chat_message'

    def __str__(self):
        return f"{self.id_user.nom if self.id_user else 'Anonyme'} - {self.date_envoi}"

# === RÉCOMPENSE ===
class Recompense(models.Model):
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    points = models.IntegerField()
    semaine = models.DateField()

    class Meta:
        db_table = 'recompense'

    def __str__(self):
        return f"{self.id_user.nom} - {self.points} pts"

# === STATISTIQUE ===
class Statistique(models.Model):
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    nb_taches_done = models.IntegerField(default=0)
    temps_connexion = models.TimeField(null=True)
    date_stat = models.DateField()

    class Meta:
        db_table = 'statistique'

    def __str__(self):
        return f"{self.id_user.nom} - {self.date_stat}"

# === TUTO ===
class Tuto(models.Model):
    titre = models.CharField(max_length=100)
    instructions = models.TextField()
    id_tache = models.ForeignKey(Tache, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'tuto'

    def __str__(self):
        return self.titre

# === INVENTAIRE ===
class Inventaire(models.Model):
    nom = models.CharField(max_length=100)
    quantite = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    id_piece = models.ForeignKey(Piece, on_delete=models.SET_NULL, null=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventaire'

    def __str__(self):
        return self.nom

# === UTILISATION RESSOURCE ===
class UtilisationRessource(models.Model):
    id_inventaire = models.ForeignKey(Inventaire, on_delete=models.CASCADE)
    id_tache = models.ForeignKey(Tache, on_delete=models.CASCADE)
    quantite_utilisee = models.DecimalField(max_digits=10, decimal_places=2)
    date_utilisation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'utilisation_ressource'

    def __str__(self):
        return f"{self.id_inventaire.nom} - {self.quantite_utilisee}"

# === ÉVÉNEMENT ===
class Evenement(models.Model):
    titre = models.CharField(max_length=100)
    description = models.TextField()
    date_debut = models.DateField()
    date_fin = models.DateField(null=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'evenement'

    def __str__(self):
        return self.titre

# === TÂCHE ÉVÉNEMENT ===
class TacheEvenement(models.Model):
    id_evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE)
    id_tache = models.ForeignKey(Tache, on_delete=models.CASCADE)

    class Meta:
        db_table = 'tache_evenement'

    def __str__(self):
        return f"{self.id_evenement.titre} - {self.id_tache.titre}"

# === DISPOSITIF ===
class Dispositif(models.Model):
    nom = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=[
        ('capteur', 'Capteur'),
        ('lampe', 'Lampe'),
        ('thermostat', 'Thermostat')
    ])
    id_piece = models.ForeignKey(Piece, on_delete=models.SET_NULL, null=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)
    etat = models.BooleanField(default=False)

    class Meta:
        db_table = 'dispositif'

    def __str__(self):
        return self.nom

# === ACTION DISPOSITIF ===
class ActionDispositif(models.Model):
    id_dispositif = models.ForeignKey(Dispositif, on_delete=models.CASCADE)
    id_tache = models.ForeignKey(Tache, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=[
        ('allumer', 'Allumer'),
        ('eteindre', 'Éteindre')
    ])
    date_execution = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'action_dispositif'

    def __str__(self):
        return f"{self.id_dispositif.nom} - {self.action}"

# === DÉPENSE ===
class Depense(models.Model):
    description = models.CharField(max_length=100)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_depense = models.DateField()
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)
    id_user = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'depense'

    def __str__(self):
        return self.description

# === BUDGET ===
class Budget(models.Model):
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    montant_restant = models.DecimalField(max_digits=10, decimal_places=2)
    periode = models.CharField(max_length=10, choices=[
        ('mois', 'Mois'),
        ('annee', 'Année')
    ])
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'budget'

    def __str__(self):
        return f"{self.periode} - {self.montant_total}"

# === HISTORIQUE TÂCHE ===
class HistoriqueTache(models.Model):
    id_tache = models.ForeignKey(Tache, on_delete=models.CASCADE)
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    date_execution = models.DateTimeField(auto_now_add=True)
    duree = models.TimeField(null=True)
    commentaire = models.TextField(blank=True)

    class Meta:
        db_table = 'historique_tache'

    def __str__(self):
        return f"{self.id_tache.titre} - {self.id_user.nom}"

# === SUGGESTION TÂCHE ===
class SuggestionTache(models.Model):
    titre = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    priorite = models.CharField(max_length=20, choices=[
        ('Haute', 'Haute'),
        ('Moyenne', 'Moyenne'),
        ('Basse', 'Basse')
    ], null=True)
    id_foyer = models.ForeignKey(Foyer, on_delete=models.SET_NULL, null=True)
    date_suggestion = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=[
        ('proposee', 'Proposée'),
        ('acceptee', 'Acceptée'),
        ('rejetee', 'Rejetée')
    ])

    class Meta:
        db_table = 'suggestion_tache'

    def __str__(self):
        return self.titre

# === PRÉFÉRENCE UTILISATEUR ===
class PreferenceUtilisateur(models.Model):
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    type_tache = models.CharField(max_length=50, choices=[
        ('nettoyage', 'Nettoyage'),
        ('cuisine', 'Cuisine'),
        ('courses', 'Courses'),
        ('entretien', 'Entretien')
    ])
    preference = models.CharField(max_length=20, choices=[
        ('aime', 'Aime'),
        ('desapprouve', 'Désapprouve')
    ])
    disponibilite = models.CharField(max_length=20, choices=[
        ('matin', 'Matin'),
        ('soir', 'Soir'),
        ('jour', 'Jour')
    ])

    class Meta:
        db_table = 'preference_utilisateur'

    def __str__(self):
        return f"{self.id_user.nom} - {self.type_tache}"

# === INTERACTION IA ===
class InteractionIa(models.Model):
    id_user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    commande = models.TextField()
    reponse = models.TextField(blank=True)
    date_interaction = models.DateTimeField(auto_now_add=True)
    id_tache = models.ForeignKey(Tache, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'interaction_ia'

    def __str__(self):
        return f"{self.id_user.nom} - {self.date_interaction}"