from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Theme
from .serializers import (
    ThemeListSerializer, ThemeDetailSerializer, ThemeCreateSerializer,
    ThemeUpdateSerializer, ThemeValidationSerializer, ThemeTestSimilaritySerializer,
    ThemeSubmitSerializer
)
from ..notifications.models import Notification
from ..history.models import History
from django.contrib.auth import get_user_model

User = get_user_model()


class ThemeListView(generics.ListAPIView):
    """
    Liste tous les thèmes avec filtrage.
    """
    queryset = Theme.objects.all()
    serializer_class = ThemeListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut', 'departement']
    search_fields = ['titre', 'description', 'mots_cles', 'etudiant__first_name', 'etudiant__last_name']
    ordering_fields = ['created_at', 'date_soumission', 'score_similarite']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Theme.objects.filter(est_test_prive=False)
        
        # Filtrer selon le rôle
        if user.is_etudiant:
            queryset = queryset.filter(etudiant=user)
        elif user.is_chef_departement:
            queryset = queryset.filter(
                departement=user.departement,
                statut__in=['SOUMIS', 'EN_REVUE_CHEF', 'EN_REVUE_DA', 'VALIDE', 'REJETE_CHEF']
            )
        elif user.is_da:
            queryset = queryset.filter(
                statut__in=['EN_REVUE_DA', 'VALIDE', 'REJETE_DA', 'REJETE_DEFINITIF']
            )
        
        return queryset.select_related('etudiant', 'rejete_par')


class ThemeDetailView(generics.RetrieveAPIView):
    """
    Détail d'un thème.
    """
    queryset = Theme.objects.all()
    serializer_class = ThemeDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Theme.objects.all()
        
        if user.is_etudiant:
            queryset = queryset.filter(etudiant=user)
        elif user.is_chef_departement:
            queryset = queryset.filter(departement=user.departement)
        
        return queryset.select_related('etudiant', 'rejete_par')


class ThemeCreateView(generics.CreateAPIView):
    """
    Création d'un nouveau thème.
    """
    queryset = Theme.objects.all()
    serializer_class = ThemeCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        user = self.request.user
        # Utiliser le departement du formulaire s'il est fourni, sinon celui de l'utilisateur
        departement = serializer.validated_data.get('departement', user.departement)
        theme = serializer.save(
            etudiant=user,
            departement=departement
        )
        
        # Créer une entrée dans l'historique
        History.objects.create(
            user=user,
            action=History.Action.CREATION,
            entity_type=History.EntityType.THEME,
            entity_id=theme.id,
            details=f"Thème créé: {theme.titre}",
            departement=departement
        )
        
        return theme
    
    def create(self, request, *args, **kwargs):
        """Créer et optionnellement soumettre le thème."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        theme = self.perform_create(serializer)
        
        # Si soumission demandée, soumettre le thème
        if request.data.get('soumettre'):
            if theme.statut in ['BROUILLON', 'REJETE_CHEF']:
                theme.soumettre()
                
                # Notifier les chefs
                chefs = User.objects.filter(
                    role='CHEF_DEPARTEMENT',
                    departement=theme.departement
                )
                for chef in chefs:
                    Notification.objects.create(
                        user=chef,
                        type='NOUVEAU_THEME',
                        titre='Nouveau thème soumis',
                        message=f"{request.user.get_full_name()} a soumis un nouveau thème: {theme.titre}",
                        lien=f'/themes/{theme.id}'
                    )
                
                # Ajouter à l'historique
                History.objects.create(
                    user=request.user,
                    action=History.Action.SOUMISSION,
                    entity_type=History.EntityType.THEME,
                    entity_id=theme.id,
                    details=f"Thème soumis: {theme.titre}",
                    departement=theme.departement
                )
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ThemeUpdateView(generics.UpdateAPIView):
    """
    Mise à jour d'un thème.
    Uniquement possible si le thème est en brouillon ou rejeté.
    """
    queryset = Theme.objects.all()
    serializer_class = ThemeUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Theme.objects.filter(
            etudiant=user,
            statut__in=['BROUILLON', 'REJETE_CHEF']
        )


class ThemeDeleteView(generics.DestroyAPIView):
    """
    Suppression d'un thème.
    Uniquement possible si le thème est en brouillon ou test privé.
    """
    queryset = Theme.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Theme.objects.filter(
            etudiant=user,
            statut__in=['BROUILLON', 'REJETE_CHEF'],
            est_test_prive=True
        )


class ThemeSubmitView(APIView):
    """
    Soumettre un thème pour validation.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        theme = get_object_or_404(Theme, pk=pk, etudiant=request.user)
        
        serializer = ThemeSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if not serializer.validated_data['confirmation']:
            return Response(
                {"error": "Vous devez confirmer la soumission."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if theme.statut not in ['BROUILLON', 'REJETE_CHEF']:
            return Response(
                {"error": "Ce thème ne peut pas être soumis dans son état actuel."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        theme.soumettre()
        
        # Notifier le chef de département
        chefs = User.objects.filter(
            role='CHEF_DEPARTEMENT',
            departement=theme.departement
        )
        
        for chef in chefs:
            Notification.objects.create(
                user=chef,
                type='NOUVEAU_THEME',
                titre='Nouveau thème soumis',
                message=f"{request.user.get_full_name()} a soumis un nouveau thème: {theme.titre}",
                lien=f'/themes/{theme.id}'
            )
        
        return Response(
            {"message": "Thème soumis avec succès."},
            status=status.HTTP_200_OK
        )


class ThemeValidateView(APIView):
    """
    Valider ou rejeter un thème (Chef ou DA).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        theme = get_object_or_404(Theme, pk=pk)
        user = request.user
        
        serializer = ThemeValidationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        action = serializer.validated_data['action']
        motif_rejet = serializer.validated_data.get('motif_rejet', '')
        
        if user.is_chef_departement:
            if theme.departement != user.departement:
                return Response(
                    {"error": "Vous n'avez pas accès à ce thème."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if theme.statut not in ['SOUMIS', 'EN_REVUE_CHEF']:
                return Response(
                    {"error": "Ce thème ne peut pas être traité actuellement."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if action == 'valider':
                theme.valider_par_chef(user)
                
                # Notifier le DA
                da_users = User.objects.filter(role='DA')
                for da in da_users:
                    Notification.objects.create(
                        user=da,
                        type='THEME_A_VALIDER',
                        titre='Thème à valider',
                        message=f"Le thème '{theme.titre}' a été validé par le Chef de département et attend votre validation.",
                        lien=f'/themes/{theme.id}'
                    )
                
                message = "Thème validé et transmis au DA."
            else:
                theme.rejeter_par_chef(user, motif_rejet)
                
                Notification.objects.create(
                    user=theme.etudiant,
                    type='THEME_REJETE',
                    titre='Thème rejeté',
                    message=f"Votre thème '{theme.titre}' a été rejeté par le Chef de département. Motif: {motif_rejet}",
                    lien=f'/themes/{theme.id}'
                )
                
                message = "Thème rejeté. L'étudiant a été notifié."
        
        elif user.is_da:
            if theme.statut not in ['EN_REVUE_DA', 'VALIDE', 'REJETE_DA']:
                return Response(
                    {"error": "Ce thème ne peut pas être traité actuellement."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if action == 'valider':
                if theme.score_similarite > 25:
                    return Response(
                        {
                            "error": "Le score de similarité dépasse 25%. Validation non recommandée.",
                            "score_similarite": theme.score_similarite
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                theme.valider_par_da(user)
                
                Notification.objects.create(
                    user=theme.etudiant,
                    type='THEME_VALIDE',
                    titre='Thème validé définitivement',
                    message=f"Félicitations ! Votre thème '{theme.titre}' a été validé définitivement par le DA. Vous pouvez maintenant soumettre votre rapport.",
                    lien=f'/themes/{theme.id}'
                )
                
                message = "Thème validé définitivement. L'étudiant a été notifié."
            else:
                theme.rejeter_par_da(user, motif_rejet)
                
                chefs = User.objects.filter(
                    role='CHEF_DEPARTEMENT',
                    departement=theme.departement
                )
                
                for chef in chefs:
                    Notification.objects.create(
                        user=chef,
                        type='THEME_REJETE_DA',
                        titre='Thème rejeté par le DA',
                        message=f"Le thème '{theme.titre}' a été rejeté définitivement par le DA. Motif: {motif_rejet}",
                        lien=f'/themes/{theme.id}'
                    )
                
                Notification.objects.create(
                    user=theme.etudiant,
                    type='THEME_REJETE_DEFINITIF',
                    titre='Thème rejeté définitivement',
                    message=f"Votre thème '{theme.titre}' a été rejeté définitivement par le DA. Motif: {motif_rejet}",
                    lien=f'/themes/{theme.id}'
                )
                
                message = "Thème rejeté définitivement. Le Chef de département et l'étudiant ont été notifiés."
        else:
            return Response(
                {"error": "Vous n'avez pas les permissions pour cette action."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response({"message": message}, status=status.HTTP_200_OK)


class ThemeCheckSimilarityView(APIView):
    """
    Vérifier la similarité d'un thème avant création (sans sauvegarder).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        titre = request.data.get('titre', '')
        description = request.data.get('description', '')
        
        if not titre:
            return Response(
                {"error": "Le titre est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rechercher les thèmes similaires par titre
        from ..utils.theme_similarity import ThemeSimilarityChecker
        from .models import Theme
        
        checker = ThemeSimilarityChecker()
        
        # Chercher les thèmes existants similaires
        similar_themes = []
        existing_themes = Theme.objects.filter(est_test_prive=False)
        
        for theme in existing_themes:
            score = checker.calculate_text_similarity(titre, theme.titre)
            if score > 30:  # Seulement si similarité > 30%
                similar_themes.append({
                    'id': theme.id,
                    'titre': theme.titre,
                    'similarity': round(score, 1)
                })
        
        # Trier par similarité décroissante
        similar_themes.sort(key=lambda x: x['similarity'], reverse=True)
        
        return Response({
            'has_similar_themes': len(similar_themes) > 0,
            'similar_themes': similar_themes[:5],  # Max 5 résultats
            'score_global': round(checker.calculate_text_similarity(titre, description), 1) if description else 0
        }, status=status.HTTP_200_OK)


class ThemeTestSimilarityView(APIView):
    """
    Tester la similarité d'un thème avec les thèmes existants.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        theme = get_object_or_404(Theme, pk=pk)
        user = request.user
        
        if user.is_etudiant and theme.etudiant != user:
            return Response(
                {"error": "Vous ne pouvez tester que vos propres thèmes."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ThemeTestSimilaritySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Rechercher les thèmes similaires
        from ..utils.theme_similarity import ThemeSimilarityChecker
        checker = ThemeSimilarityChecker()
        result = checker.check_similarity(theme)
        
        theme.score_similarite = result['score_global']
        theme.themes_similaires = result['themes_similaires']
        theme.save()
        
        return Response(result, status=status.HTTP_200_OK)


class EtudiantThemeListView(generics.ListAPIView):
    """
    Liste les thèmes de l'étudiant connecté.
    """
    serializer_class = ThemeListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Theme.objects.filter(
            etudiant=self.request.user,
            est_test_prive=False
        ).select_related('etudiant')


class EtudiantThemeTestListView(generics.ListAPIView):
    """
    Liste les tests privés de thèmes de l'étudiant.
    """
    serializer_class = ThemeListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Theme.objects.filter(
            etudiant=self.request.user,
            est_test_prive=True
        ).select_related('etudiant')


class ThemeStatisticsView(APIView):
    """
    Statistiques sur les thèmes.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.is_etudiant:
            queryset = Theme.objects.filter(etudiant=user, est_test_prive=False)
        elif user.is_chef_departement:
            queryset = Theme.objects.filter(departement=user.departement, est_test_prive=False)
        else:
            queryset = Theme.objects.filter(est_test_prive=False)
        
        stats = {
            'total': queryset.count(),
            'soumis': queryset.filter(statut='SOUMIS').count(),
            'en_revue': queryset.filter(statut__in=['EN_REVUE_CHEF', 'EN_REVUE_DA']).count(),
            'valides': queryset.filter(statut='VALIDE').count(),
            'rejetes': queryset.filter(statut__in=['REJETE_CHEF', 'REJETE_DA', 'REJETE_DEFINITIF']).count(),
            'similarite_elevee': queryset.filter(score_similarite__gt=25).count(),
            'score_moyen_similarite': queryset.filter(score_similarite__gt=0).aggregate(
                avg_score=models.Avg('score_similarite')
            )['avg_score'] or 0
        }
        
        return Response(stats)
