from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Tache, Foyer, Utilisateur, StatutTache, Invitation, Piece
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.db.models import Count

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

    foyers = Foyer.objects.all()  # ← SUPPRIMÉ .annotate()
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

        statut = StatutTache.objects.get(id=id_statut) if id_statut else StatutTache.objects.first()
        piece = Piece.objects.get(id=id_piece) if id_piece else None

        tache = Tache(
            titre=titre,
            description=description,
            date_limite=date_limite,
            priorite=priorite,
            id_statut=statut,
            id_foyer=request.user.id_foyer,  # ← FOYER DE L'UTILISATEUR
            id_piece=piece
        )
        tache.save()
        messages.success(request, "Tâche ajoutée avec succès !")
        return redirect('liste_taches')

    statuts = StatutTache.objects.all()
    pieces = Piece.objects.filter(id_foyer=request.user.id_foyer)
    return render(request, 'maison_app/ajouter_tache.html', {
        'statuts': statuts,
        'pieces': pieces
    })
@login_required
def supprimer_tache(request, tache_id):
    tache = get_object_or_404(Tache, id=tache_id, id_foyer=request.user.id_foyer)  # ← CORRIGÉ

    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent supprimer une tâche.")
        return redirect('liste_taches')
    
    if request.method == 'POST':
        tache.delete()
        messages.success(request, "Tâche supprimée avec succès !")
        return redirect('liste_taches')
    
    return render(request, 'maison_app/supprimer_tache.html', {'tache': tache})
@login_required
def creer_foyer(request):
    if request.user.role != 'admin':
        messages.error(request, "Accès refusé.")
        return redirect('liste_foyers')

    if request.method == 'POST':
        nom = request.POST['nom']
        nb_pieces = request.POST.get('nb_pieces', 0)
        foyer = Foyer(nom=nom, nb_pieces=nb_pieces)
        foyer.save()

        # Associe l'admin au foyer
        request.user.id_foyer = foyer
        request.user.save()

        messages.success(request, f"Foyer '{nom}' créé !")
        return redirect('liste_foyers')
    
    return render(request, 'maison_app/creer_foyer.html')

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

# === ADMIN : Générer un code d'invitation ===
@login_required
def generer_invitation(request, foyer_id):
    if request.user.role != 'admin':
        messages.error(request, "Accès refusé. Seuls les administrateurs peuvent inviter.")
        return redirect('liste_foyers')

    foyer = get_object_or_404(Foyer, id=foyer_id)
    role = request.POST.get('role', 'membre')

    invitation = Invitation.objects.create(
        foyer=foyer,
        role=role,
        cree_par=request.user
    )
    messages.success(request, f"Code d'invitation : <strong>{invitation.code}</strong>")
    return redirect('liste_foyers')
@login_required
def ajouter_piece(request):
    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent ajouter une pièce.")
        return redirect('liste_foyers')

    # Vérifie que l'admin a un foyer
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

# === PUBLIC : Rejoindre avec un code ===
def rejoindre_foyer(request):
    if request.method == 'POST':
        code = request.POST['code']
        try:
            invitation = Invitation.objects.get(code=code, utilise=False)
            if invitation.est_valide():
                utilisateur = Utilisateur(
                    nom=request.POST['nom'],
                    email=request.POST['email'],
                    role=invitation.role,
                    id_foyer=invitation.foyer
                )
                utilisateur.save()
                invitation.utilise = True
                invitation.save()
                messages.success(request, f"Bienvenue dans le foyer {invitation.foyer.nom} !")
                return redirect('liste_taches')
            else:
                messages.error(request, "Ce code est expiré ou déjà utilisé.")
        except Invitation.DoesNotExist:
            messages.error(request, "Code invalide.")
    return render(request, 'maison_app/rejoindre.html')