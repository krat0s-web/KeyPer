from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Tache, Foyer, Utilisateur, StatutTache, Invitation, Piece, Animal  # ← IMPORTS COMPLETS
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth import logout
from .models import ROLE_CHOICES  # ← AJOUTEZ CET IMPORT


# === CONNEXION PERSONNALISÉE ===
def custom_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', '/taches/')
                return redirect(next_url)
            else:
                messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

# === VUES PROTÉGÉES ===
@login_required
def liste_taches(request):
    taches = Tache.objects.all()
    return render(request, 'maison_app/liste_taches.html', {'taches': taches})

@login_required
def liste_foyers(request):
    if request.method == 'POST' and 'foyer_id' in request.POST:
        if request.user.role != 'admin':
            messages.error(request, "Accès refusé.")
            return redirect('liste_foyers')

        foyer_id = request.POST['foyer_id']
        nom_piece = request.POST['nom_piece']
        foyer = get_object_or_404(Foyer, id=foyer_id)

        Piece.objects.create(nom=nom_piece, id_foyer=foyer)
        messages.success(request, f"Pièce '{nom_piece}' ajoutée !")
        return redirect('liste_foyers')

    foyers = Foyer.objects.prefetch_related('pieces', 'animaux')  # ← AJOUTÉ prefetch_related
    return render(request, 'maison_app/liste_foyers.html', {'foyers': foyers})

@login_required
def liste_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all()
    return render(request, 'maison_app/liste_utilisateurs.html', {'utilisateurs': utilisateurs})

@login_required
def ajouter_tache(request):
    if request.method == 'POST':
        titre = request.POST['titre']
        description = request.POST.get('description', '')
        date_limite = request.POST.get('date_limite')
        priorite = request.POST.get('priorite')
        id_statut = request.POST.get('id_statut')
        id_piece = request.POST.get('id_piece')
        id_animal = request.POST.get('id_animal')

        statut = StatutTache.objects.get(id=id_statut) if id_statut else StatutTache.objects.first()
        piece = Piece.objects.get(id=id_piece) if id_piece else None
        animal = Animal.objects.get(id=id_animal) if id_animal else None

        tache = Tache(
            titre=titre,
            description=description,
            date_limite=date_limite,
            priorite=priorite,
            id_statut=statut,
            id_foyer=request.user.id_foyer,
            id_piece=piece,
            id_animal=animal
        )
        tache.save()
        messages.success(request, "Tâche ajoutée avec succès !")
        return redirect('liste_taches')

    statuts = StatutTache.objects.all()
    pieces = Piece.objects.filter(id_foyer=request.user.id_foyer)
    animaux = Animal.objects.filter(id_foyer=request.user.id_foyer)
    return render(request, 'maison_app/ajouter_tache.html', {
        'statuts': statuts,
        'pieces': pieces,
        'animaux': animaux
    })

@login_required
def creer_foyer(request):
    if request.user.role != 'admin':
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')

    if request.method == 'POST':
        nom = request.POST['nom']
        foyer = Foyer(nom=nom)
        foyer.save()

        # Associe l'admin au foyer
        request.user.id_foyer = foyer
        request.user.save()

        messages.success(request, f"Foyer '{nom}' créé !")
        return redirect('liste_foyers')
    
    return render(request, 'maison_app/creer_foyer.html')

@login_required
def ajouter_piece(request):
    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent ajouter une pièce.")
        return redirect('liste_foyers')

    if not request.user.id_foyer:
        messages.error(request, "Vous devez d'abord créer un foyer.")
        return redirect('creer_foyer')

    if request.method == 'POST':
        nom = request.POST['nom']
        piece = Piece(nom=nom, id_foyer=request.user.id_foyer)
        piece.save()
        messages.success(request, f"Pièce '{nom}' ajoutée !")
        return redirect('liste_foyers')

    return render(request, 'maison_app/ajouter_piece.html')

@login_required
def ajouter_animal(request):
    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent ajouter un animal.")
        return redirect('liste_foyers')

    if not request.user.id_foyer:
        messages.error(request, "Vous devez d'abord créer un foyer.")
        return redirect('creer_foyer')

    if request.method == 'POST':
        nom = request.POST['nom']
        id_piece = request.POST.get('id_piece')

        # Récupérez l'instance Piece (CORRIGÉ)
        piece = Piece.objects.get(id=id_piece) if id_piece else None

        animal = Animal(
            nom=nom,
            id_foyer=request.user.id_foyer,
            id_piece=piece  # ← CORRIGÉ : instance Piece
        )
        animal.save()
        messages.success(request, f"Animal '{nom}' ajouté !")
        return redirect('liste_foyers')

    pieces = Piece.objects.filter(id_foyer=request.user.id_foyer)
    return render(request, 'maison_app/ajouter_animal.html', {'pieces': pieces})

@login_required
def supprimer_tache(request, tache_id):
    tache = get_object_or_404(Tache, id=tache_id, id_foyer=request.user.id_foyer)

    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent supprimer une tâche.")
        return redirect('liste_taches')
    
    if request.method == 'POST':
        tache.delete()
        messages.success(request, "Tâche supprimée avec succès !")
        return redirect('liste_taches')
    
    return render(request, 'maison_app/supprimer_tache.html', {'tache': tache})

@login_required
def supprimer_foyer(request, foyer_id):
    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent supprimer un foyer.")
        return redirect('liste_foyers')

    foyer = get_object_or_404(Foyer, id=foyer_id)

    if request.method == 'POST':
        nom = foyer.nom
        foyer.delete()
        messages.success(request, f"Foyer '{nom}' supprimé avec succès !")
        return redirect('liste_foyers')

    return render(request, 'maison_app/supprimer_foyer.html', {'foyer': foyer})

@login_required
def generer_invitation(request, foyer_id):
    if request.user.role != 'admin':
        messages.error(request, "Accès refusé. Seuls les administrateurs peuvent inviter.")
        return redirect('liste_foyers')

    foyer = get_object_or_404(Foyer, id=foyer_id)
    if request.method == 'POST':
        role = request.POST.get('role', 'membre')
        invitation = Invitation.objects.create(
            foyer=foyer,
            role=role,
            cree_par=request.user
        )
        messages.success(request, f"Code d'invitation : <strong>{invitation.code}</strong>")
        return redirect('liste_foyers')

    # ← ENVOYEZ ROLE_CHOICES AU TEMPLATE
    return render(request, 'maison_app/generer_invitation.html', {
        'foyer': foyer,
        'ROLE_CHOICES': ROLE_CHOICES
    })

@login_required
def liste_utilisateurs_par_foyer(request):
    if request.user.role != 'admin':
        messages.error(request, "Accès refusé. Seuls les administrateurs peuvent voir cette page.")
        return redirect('liste_taches')

    foyers = Foyer.objects.all().prefetch_related('utilisateur_set')  # Charge les utilisateurs
    return render(request, 'maison_app/liste_utilisateurs_par_foyer.html', {'foyers': foyers})

@login_required
def detail_foyer(request, foyer_id):
    foyer = get_object_or_404(Foyer, id=foyer_id)
    if foyer != request.user.id_foyer:
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')

    # === AJOUT DE PIÈCE (POST) ===
    if request.method == 'POST' and 'nom_piece' in request.POST:
        if request.user.role != 'admin':
            messages.error(request, "Accès refusé.")
            return redirect('detail_foyer', foyer_id=foyer_id)

        nom = request.POST['nom_piece']
        piece = Piece(nom=nom, id_foyer=foyer)
        piece.save()
        messages.success(request, f"Pièce '{nom}' ajoutée !")
        return redirect('detail_foyer', foyer_id=foyer_id)

    # Charge les pièces et animaux
    foyer = Foyer.objects.prefetch_related('pieces', 'animaux').get(id=foyer_id)
    return render(request, 'maison_app/detail_foyer.html', {'foyer': foyer})
@login_required
def custom_logout(request):
    logout(request)
    messages.success(request, "Vous êtes déconnecté !")
    return redirect('/taches/')  # ou '/' si vous voulez la page d'accueil

@login_required
def supprimer_membre(request, user_id):
    if request.user.role != 'admin':
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')

    membre = get_object_or_404(Utilisateur, id=user_id, id_foyer=request.user.id_foyer)

    if request.method == 'POST':
        membre.delete()
        messages.success(request, f"Membre {membre.email} supprimé !")
        return redirect('detail_foyer', foyer_id=request.user.id_foyer.id)

    return render(request, 'maison_app/supprimer_membre.html', {'membre': membre})


def rejoindre_foyer(request):
    if request.method == 'POST':
        code = request.POST['code']
        nom = request.POST['nom']
        email = request.POST['email']

        try:
            invitation = Invitation.objects.get(code=code, utilise=False)
            if invitation.est_valide():
                # Vérifie si l'email existe déjà
                if Utilisateur.objects.filter(email=email).exists():
                    messages.error(request, "Cet email est déjà utilisé.")
                    return render(request, 'maison_app/rejoindre.html')

                # Crée l'utilisateur avec username = email
                utilisateur = Utilisateur(
                    username=email,  # ← AJOUTÉ
                    email=email,
                    nom=nom,
                    role=invitation.role,
                    id_foyer=invitation.foyer
                )
                utilisateur.set_password('temporary123')  # Mot de passe temporaire
                utilisateur.save()

                invitation.utilise = True
                invitation.save()

                messages.success(request, f"Bienvenue {nom} dans le foyer {invitation.foyer.nom} !")
                login(request, utilisateur)  # Connexion automatique
                return redirect('liste_taches')
            else:
                messages.error(request, "Code expiré ou déjà utilisé.")
        except Invitation.DoesNotExist:
            messages.error(request, "Code invalide.")
    
    return render(request, 'maison_app/rejoindre.html')

@login_required
def terminer_tache(request, tache_id):
    tache = get_object_or_404(Tache, id=tache_id, id_foyer=request.user.id_foyer)
    if tache.terminee:
        messages.error(request, "Tâche déjà terminée.")
        return redirect('detail_foyer', foyer_id=tache.id_foyer.id)

    tache.terminee = True
    tache.complete_par = request.user
    tache.save()
    messages.success(request, "Tâche terminée !")
    return redirect('detail_foyer', foyer_id=tache.id_foyer.id)
# === INSCRIPTION (NOUVELLE PAGE) ===
def inscription(request):
    if request.method == 'POST':
        nom = request.POST['nom']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'registration/inscription.html')

        if Utilisateur.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'registration/inscription.html')

        user = Utilisateur.objects.create_user(
            email=email,
            username=email,
            nom=nom,
            password=password,
            role='membre'
        )
        login(request, user)
        messages.success(request, f"Bienvenue {nom} ! Votre compte est créé.")
        return redirect('liste_taches')

    return render(request, 'registration/inscription.html')