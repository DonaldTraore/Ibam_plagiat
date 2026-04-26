from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Count, Avg, Q
from django.contrib.auth import get_user_model
from plagiarism_detection.reports.models import Report
from plagiarism_detection.themes.models import Theme
from plagiarism_detection.notifications.models import Notification
from plagiarism_detection.history.models import History

User = get_user_model()


class DashboardView(APIView):
    """
    Vue d'ensemble du tableau de bord.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        data = {
            'user': {
                'id': user.id,
                'full_name': user.get_full_name(),
                'role': user.role,
                'role_display': user.get_role_display(),
                'departement': user.departement,
            },
            'notifications': self._get_notifications(user),
            'recent_activities': self._get_recent_activities(user),
            'statistics': self._get_statistics(user),
            'pending_actions': self._get_pending_actions(user),
        }
        
        return Response(data)
    
    def _get_notifications(self, user):
        """Récupère les notifications non lues récentes."""
        return Notification.objects.filter(
            user=user,
            lu=False
        ).order_by('-created_at')[:5].values('id', 'titre', 'message', 'type', 'created_at')
    
    def _get_recent_activities(self, user):
        """Récupère les activités récentes."""
        queryset = History.objects.all()
        
        if user.is_etudiant:
            queryset = queryset.filter(user=user)
        elif user.is_chef_departement:
            queryset = queryset.filter(departement=user.departement)
        
        return queryset.order_by('-created_at')[:10].values(
            'action', 'entity_type', 'details', 'created_at'
        )
    
    def _get_statistics(self, user):
        """Calcule les statistiques selon le rôle."""
        stats = {}
        
        if user.is_etudiant:
            # Stats pour l'étudiant
            stats = {
                'mes_rapports': {
                    'total': Report.objects.filter(etudiant=user, est_test_prive=False).count(),
                    'valides': Report.objects.filter(etudiant=user, statut='VALIDE').count(),
                    'rejetes': Report.objects.filter(
                        etudiant=user,
                        statut__in=['REJETE_CHEF', 'REJETE_DA', 'REJETE_DEFINITIF']
                    ).count(),
                    'en_attente': Report.objects.filter(
                        etudiant=user,
                        statut__in=['SOUMIS', 'EN_REVUE_CHEF', 'EN_REVUE_DA']
                    ).count(),
                },
                'mes_themes': {
                    'total': Theme.objects.filter(etudiant=user, est_test_prive=False).count(),
                    'valides': Theme.objects.filter(etudiant=user, statut='VALIDE').count(),
                    'en_attente': Theme.objects.filter(
                        etudiant=user,
                        statut__in=['SOUMIS', 'EN_REVUE_CHEF', 'EN_REVUE_DA']
                    ).count(),
                },
                'plagiat_moyen': Report.objects.filter(
                    etudiant=user,
                    score_plagiat_global__gt=0
                ).aggregate(avg=Avg('score_plagiat_global'))['avg'] or 0
            }
        
        elif user.is_chef_departement:
            # Stats pour le chef de département
            stats = {
                'rapports': {
                    'total': Report.objects.filter(departement=user.departement).count(),
                    'a_traiter': Report.objects.filter(
                        departement=user.departement,
                        statut__in=['SOUMIS', 'EN_REVUE_CHEF']
                    ).count(),
                    'valides': Report.objects.filter(
                        departement=user.departement,
                        statut='VALIDE'
                    ).count(),
                    'plagiat_detecte': Report.objects.filter(
                        departement=user.departement,
                        est_plagiat=True
                    ).count(),
                },
                'themes': {
                    'total': Theme.objects.filter(departement=user.departement).count(),
                    'a_traiter': Theme.objects.filter(
                        departement=user.departement,
                        statut__in=['SOUMIS', 'EN_REVUE_CHEF']
                    ).count(),
                },
                'etudiants': User.objects.filter(
                    role='ETUDIANT',
                    departement=user.departement
                ).count()
            }
        
        elif user.is_da:
            # Stats pour le DA
            stats = {
                'rapports': {
                    'total': Report.objects.count(),
                    'a_valider': Report.objects.filter(
                        statut__in=['EN_REVUE_DA', 'VALIDE', 'REJETE_DA']
                    ).count(),
                    'valides': Report.objects.filter(statut='VALIDE').count(),
                },
                'themes': {
                    'total': Theme.objects.count(),
                    'a_valider': Theme.objects.filter(
                        statut__in=['EN_REVUE_DA', 'VALIDE', 'REJETE_DA']
                    ).count(),
                },
                'rejets_definitifs': {
                    'rapports': Report.objects.filter(statut='REJETE_DEFINITIF').count(),
                    'themes': Theme.objects.filter(statut='REJETE_DEFINITIF').count(),
                }
            }
        
        return stats
    
    def _get_pending_actions(self, user):
        """Récupère les actions en attente selon le rôle."""
        actions = []
        
        if user.is_chef_departement:
            # Rapports à valider
            rapports = Report.objects.filter(
                departement=user.departement,
                statut__in=['SOUMIS', 'EN_REVUE_CHEF']
            )
            for rapport in rapports[:5]:
                actions.append({
                    'type': 'VALIDATION_RAPPORT',
                    'titre': f"Valider le rapport: {rapport.titre}",
                    'entity_id': rapport.id,
                    'created_at': rapport.date_soumission,
                })
            
            # Thèmes à valider
            themes = Theme.objects.filter(
                departement=user.departement,
                statut__in=['SOUMIS', 'EN_REVUE_CHEF']
            )
            for theme in themes[:5]:
                actions.append({
                    'type': 'VALIDATION_THEME',
                    'titre': f"Valider le thème: {theme.titre}",
                    'entity_id': theme.id,
                    'created_at': theme.date_soumission,
                })
        
        elif user.is_da:
            # Rapports en attente de validation finale
            rapports = Report.objects.filter(statut='EN_REVUE_DA')
            for rapport in rapports[:5]:
                actions.append({
                    'type': 'VALIDATION_FINALE_RAPPORT',
                    'titre': f"Valider définitivement: {rapport.titre}",
                    'entity_id': rapport.id,
                    'created_at': rapport.date_validation_chef,
                })
            
            # Thèmes en attente de validation finale
            themes = Theme.objects.filter(statut='EN_REVUE_DA')
            for theme in themes[:5]:
                actions.append({
                    'type': 'VALIDATION_FINALE_THEME',
                    'titre': f"Valider définitivement: {theme.titre}",
                    'entity_id': theme.id,
                    'created_at': theme.date_validation_chef,
                })
        
        return sorted(actions, key=lambda x: x['created_at'], reverse=True)[:10]


class DashboardStatsView(APIView):
    """
    Statistiques détaillées pour le tableau de bord.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Période (par défaut: tous les temps)
        periode = request.query_params.get('periode', 'all')
        
        data = {
            'plagiat_evolution': self._get_plagiat_evolution(user, periode),
            'statuts_repartition': self._get_statuts_repartition(user),
            'top_plagiat': self._get_top_plagiat(user),
        }
        
        return Response(data)
    
    def _get_plagiat_evolution(self, user, periode):
        """Récupère l'évolution des scores de plagiat."""
        from django.db.models.functions import TruncMonth
        
        queryset = Report.objects.filter(score_plagiat_global__gt=0)
        
        if user.is_etudiant:
            queryset = queryset.filter(etudiant=user)
        elif user.is_chef_departement:
            queryset = queryset.filter(departement=user.departement)
        
        evolution = queryset.annotate(
            mois=TruncMonth('created_at')
        ).values('mois').annotate(
            moyenne_score=Avg('score_plagiat_global'),
            nombre_rapports=Count('id')
        ).order_by('mois')
        
        return list(evolution)
    
    def _get_statuts_repartition(self, user):
        """Récupère la répartition par statut."""
        queryset = Report.objects.filter(est_test_prive=False)
        
        if user.is_etudiant:
            queryset = queryset.filter(etudiant=user)
        elif user.is_chef_departement:
            queryset = queryset.filter(departement=user.departement)
        
        return list(queryset.values('statut').annotate(count=Count('id')))
    
    def _get_top_plagiat(self, user):
        """Récupère les rapports avec le plus haut score de plagiat."""
        queryset = Report.objects.filter(
            score_plagiat_global__gt=0
        ).order_by('-score_plagiat_global')[:10]
        
        if user.is_etudiant:
            queryset = queryset.filter(etudiant=user)
        elif user.is_chef_departement:
            queryset = queryset.filter(departement=user.departement)
        
        return list(queryset.values(
            'id', 'titre', 'score_plagiat_global', 'etudiant__first_name', 'etudiant__last_name'
        ))


class GlobalSearchView(APIView):
    """
    Recherche globale dans les rapports, thèmes et documents.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        
        if not query or len(query) < 3:
            return Response(
                {"error": "La recherche doit contenir au moins 3 caractères."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        results = {
            'rapports': [],
            'themes': [],
            'documents': [],
        }
        
        # Recherche dans les rapports
        rapports_query = Report.objects.filter(
            Q(titre__icontains=query) |
            Q(etudiant__first_name__icontains=query) |
            Q(etudiant__last_name__icontains=query) |
            Q(etudiant__email__icontains=query)
        )
        
        if user.is_etudiant:
            rapports_query = rapports_query.filter(etudiant=user)
        elif user.is_chef_departement:
            rapports_query = rapports_query.filter(departement=user.departement)
        
        results['rapports'] = list(rapports_query.values(
            'id', 'titre', 'statut', 'score_plagiat_global', 'created_at'
        )[:10])
        
        # Recherche dans les thèmes
        themes_query = Theme.objects.filter(
            Q(titre__icontains=query) |
            Q(description__icontains=query) |
            Q(mots_cles__icontains=query) |
            Q(etudiant__first_name__icontains=query) |
            Q(etudiant__last_name__icontains=query)
        )
        
        if user.is_etudiant:
            themes_query = themes_query.filter(etudiant=user)
        elif user.is_chef_departement:
            themes_query = themes_query.filter(departement=user.departement)
        
        results['themes'] = list(themes_query.values(
            'id', 'titre', 'statut', 'score_similarite', 'created_at'
        )[:10])
        
        return Response(results)


class SystemStatusView(APIView):
    """
    Statut du système.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        from plagiarism_detection.documents.models import ReferenceDocument
        
        data = {
            'total_rapports': Report.objects.count(),
            'total_themes': Theme.objects.count(),
            'total_documents_ref': ReferenceDocument.objects.filter(est_actif=True).count(),
            'total_utilisateurs': User.objects.filter(is_active=True).count(),
            'system_status': 'operational',
            'plagiarism_threshold': 25,
        }
        
        return Response(data)
