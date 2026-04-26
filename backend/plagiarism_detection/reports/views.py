from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Report, ReportChapter, PlagiarismResult
from .serializers import (
    ReportListSerializer, ReportDetailSerializer, ReportCreateSerializer,
    ReportUpdateSerializer, ReportValidationSerializer, PlagiarismTestSerializer,
    ReportSubmitSerializer, ReportChapterSerializer, PlagiarismResultSerializer
)
from ..utils.plagiarism_detector import PlagiarismDetector
from ..notifications.models import Notification


class ReportListView(generics.ListAPIView):
    """
    Liste tous les rapports avec filtrage.
    """
    queryset = Report.objects.all()
    serializer_class = ReportListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['statut', 'type_document', 'departement', 'est_plagiat']
    search_fields = ['titre', 'etudiant__first_name', 'etudiant__last_name', 'etudiant__email']
    ordering_fields = ['created_at', 'date_soumission', 'score_plagiat_global']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Report.objects.filter(est_test_prive=False)
        
        # Filtrer selon le rôle
        if user.is_etudiant:
            # Étudiant: ne voit que ses propres rapports
            queryset = queryset.filter(etudiant=user)
        elif user.is_chef_departement:
            # Chef de département: voit les rapports de son département
            queryset = queryset.filter(
                departement=user.departement,
                statut__in=['SOUMIS', 'EN_REVUE_CHEF', 'EN_REVUE_DA', 'VALIDE', 'REJETE_CHEF']
            )
        elif user.is_secretaire:
            # Secrétaire: voit tous les rapports soumis
            queryset = queryset.filter(statut__in=['SOUMIS', 'EN_REVUE_CHEF', 'EN_REVUE_DA', 'VALIDE'])
        elif user.is_da:
            # DA: voit les rapports en révision DA et validés/rejetés
            queryset = queryset.filter(
                statut__in=['EN_REVUE_DA', 'VALIDE', 'REJETE_DA', 'REJETE_DEFINITIF']
            )
        
        return queryset.select_related('etudiant').prefetch_related('chapters', 'plagiarism_results')


class ReportDetailView(generics.RetrieveAPIView):
    """
    Détail d'un rapport.
    """
    queryset = Report.objects.all()
    serializer_class = ReportDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Report.objects.all()
        
        if user.is_etudiant:
            queryset = queryset.filter(etudiant=user)
        elif user.is_chef_departement:
            queryset = queryset.filter(departement=user.departement)
        
        return queryset.select_related('etudiant', 'rejete_par').prefetch_related('chapters', 'plagiarism_results')


class ReportCreateView(generics.CreateAPIView):
    """
    Création d'un nouveau rapport.
    """
    queryset = Report.objects.all()
    serializer_class = ReportCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def perform_create(self, serializer):
        user = self.request.user
        fichier = self.request.FILES.get('fichier')
        
        # Extraire le nom original du fichier
        fichier_nom_original = fichier.name if fichier else None
        
        report = serializer.save(
            etudiant=user,
            fichier_nom_original=fichier_nom_original,
            departement=user.departement
        )
        
        return report


class ReportUpdateView(generics.UpdateAPIView):
    """
    Mise à jour d'un rapport.
    Uniquement possible si le rapport est en brouillon ou rejeté.
    """
    queryset = Report.objects.all()
    serializer_class = ReportUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Report.objects.filter(
            etudiant=user,
            statut__in=['BROUILLON', 'REJETE_CHEF']
        )


class ReportDeleteView(generics.DestroyAPIView):
    """
    Suppression d'un rapport.
    Uniquement possible si le rapport est en brouillon ou test privé.
    """
    queryset = Report.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Report.objects.filter(
            etudiant=user,
            statut__in=['BROUILLON', 'REJETE_CHEF'],
            est_test_prive=True
        )


class ReportSubmitView(APIView):
    """
    Soumettre un rapport pour validation.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk, etudiant=request.user)
        
        serializer = ReportSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if not serializer.validated_data['confirmation']:
            return Response(
                {"error": "Vous devez confirmer la soumission."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que le rapport peut être soumis
        if report.statut not in ['BROUILLON', 'REJETE_CHEF']:
            return Response(
                {"error": "Ce rapport ne peut pas être soumis dans son état actuel."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Soumettre le rapport
        report.soumettre()
        
        # Notifier le chef de département
        from django.contrib.auth import get_user_model
        User = get_user_model()
        chefs = User.objects.filter(
            role='CHEF_DEPARTEMENT',
            departement=report.departement
        )
        
        for chef in chefs:
            Notification.objects.create(
                user=chef,
                type='NOUVEAU_RAPPORT',
                titre='Nouveau rapport soumis',
                message=f"{request.user.get_full_name()} a soumis un nouveau rapport: {report.titre}",
                lien=f'/reports/{report.id}'
            )
        
        return Response(
            {"message": "Rapport soumis avec succès."},
            status=status.HTTP_200_OK
        )


class ReportValidateView(APIView):
    """
    Valider ou rejeter un rapport (Chef ou DA).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        user = request.user
        
        serializer = ReportValidationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        action = serializer.validated_data['action']
        motif_rejet = serializer.validated_data.get('motif_rejet', '')
        
        # Vérifier les permissions selon le statut
        if user.is_chef_departement:
            if report.departement != user.departement:
                return Response(
                    {"error": "Vous n'avez pas accès à ce rapport."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if report.statut not in ['SOUMIS', 'EN_REVUE_CHEF']:
                return Response(
                    {"error": "Ce rapport ne peut pas être traité actuellement."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if action == 'valider':
                report.valider_par_chef(user)
                
                # Notifier le DA
                da_users = User.objects.filter(role='DA')
                for da in da_users:
                    Notification.objects.create(
                        user=da,
                        type='RAPPORT_A_VALIDER',
                        titre='Rapport à valider',
                        message=f"Le rapport '{report.titre}' a été validé par le Chef de département et attend votre validation.",
                        lien=f'/reports/{report.id}'
                    )
                
                message = "Rapport validé et transmis au DA."
            else:
                report.rejeter_par_chef(user, motif_rejet)
                
                # Notifier l'étudiant
                Notification.objects.create(
                    user=report.etudiant,
                    type='RAPPORT_REJETE',
                    titre='Rapport rejeté',
                    message=f"Votre rapport '{report.titre}' a été rejeté par le Chef de département. Motif: {motif_rejet}",
                    lien=f'/reports/{report.id}'
                )
                
                message = "Rapport rejeté. L'étudiant a été notifié."
        
        elif user.is_da:
            if report.statut not in ['EN_REVUE_DA', 'VALIDE', 'REJETE_DA']:
                return Response(
                    {"error": "Ce rapport ne peut pas être traité actuellement."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if action == 'valider':
                # Vérifier le score de plagiat
                if report.score_plagiat_global > 25:
                    return Response(
                        {
                            "error": "Le score de plagiat dépasse 25%. Validation non recommandée.",
                            "score_plagiat": report.score_plagiat_global
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                report.valider_par_da(user)
                
                # Notifier l'étudiant
                Notification.objects.create(
                    user=report.etudiant,
                    type='RAPPORT_VALIDE',
                    titre='Rapport validé définitivement',
                    message=f"Félicitations ! Votre rapport '{report.titre}' a été validé définitivement par le DA.",
                    lien=f'/reports/{report.id}'
                )
                
                message = "Rapport validé définitivement. L'étudiant a été notifié."
            else:
                report.rejeter_par_da(user, motif_rejet)
                
                # Notifier le chef de département et l'étudiant
                chefs = User.objects.filter(
                    role='CHEF_DEPARTEMENT',
                    departement=report.departement
                )
                
                for chef in chefs:
                    Notification.objects.create(
                        user=chef,
                        type='RAPPORT_REJETE_DA',
                        titre='Rapport rejeté par le DA',
                        message=f"Le rapport '{report.titre}' a été rejeté définitivement par le DA. Motif: {motif_rejet}",
                        lien=f'/reports/{report.id}'
                    )
                
                Notification.objects.create(
                    user=report.etudiant,
                    type='RAPPORT_REJETE_DEFINITIF',
                    titre='Rapport rejeté définitivement',
                    message=f"Votre rapport '{report.titre}' a été rejeté définitivement par le DA. Motif: {motif_rejet}",
                    lien=f'/reports/{report.id}'
                )
                
                message = "Rapport rejeté définitivement. Le Chef de département et l'étudiant ont été notifiés."
        else:
            return Response(
                {"error": "Vous n'avez pas les permissions pour cette action."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response({"message": message}, status=status.HTTP_200_OK)


class ReportTestPlagiarismView(APIView):
    """
    Tester le plagiat d'un rapport.
    Accessible par l'étudiant (test privé) ou les enseignants.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        user = request.user
        
        # Vérifier les permissions
        if user.is_etudiant and report.etudiant != user:
            return Response(
                {"error": "Vous ne pouvez tester que vos propres rapports."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if user.is_chef_departement and report.departement != user.departement:
            return Response(
                {"error": "Vous n'avez pas accès à ce rapport."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PlagiarismTestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        type_detection = serializer.validated_data.get('type_detection', 'PAR_CHAPITRE')
        chapitres_specifiques = serializer.validated_data.get('chapitres_specifiques', None)
        
        # Lancer la détection de plagiat
        detector = PlagiarismDetector()
        result = detector.analyze_report(
            report,
            type_detection=type_detection,
            chapitres_specifiques=chapitres_specifiques,
            teste_par=user
        )
        
        # Mettre à jour le score global du rapport
        report.score_plagiat_global = result.score_global
        report.est_plagiat = result.depasse_seuil
        report.save()
        
        # Sérialiser et retourner le résultat
        result_serializer = PlagiarismResultSerializer(result)
        
        return Response(result_serializer.data, status=status.HTTP_200_OK)


class EtudiantReportListView(generics.ListAPIView):
    """
    Liste les rapports de l'étudiant connecté.
    """
    serializer_class = ReportListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Report.objects.filter(
            etudiant=self.request.user,
            est_test_prive=False
        ).select_related('etudiant')


class EtudiantTestPrivateListView(generics.ListAPIView):
    """
    Liste les tests privés de l'étudiant connecté.
    """
    serializer_class = ReportListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Report.objects.filter(
            etudiant=self.request.user,
            est_test_prive=True
        ).select_related('etudiant')


class PlagiarismResultDetailView(generics.RetrieveAPIView):
    """
    Détail d'un résultat de plagiat.
    """
    queryset = PlagiarismResult.objects.all()
    serializer_class = PlagiarismResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = PlagiarismResult.objects.all()
        
        if user.is_etudiant:
            queryset = queryset.filter(report__etudiant=user)
        elif user.is_chef_departement:
            queryset = queryset.filter(report__departement=user.departement)
        
        return queryset.select_related('report', 'teste_par')


class ReportStatisticsView(APIView):
    """
    Statistiques sur les rapports.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.is_etudiant:
            queryset = Report.objects.filter(etudiant=user, est_test_prive=False)
        elif user.is_chef_departement:
            queryset = Report.objects.filter(departement=user.departement, est_test_prive=False)
        else:
            queryset = Report.objects.filter(est_test_prive=False)
        
        stats = {
            'total': queryset.count(),
            'soumis': queryset.filter(statut='SOUMIS').count(),
            'en_revue': queryset.filter(statut__in=['EN_REVUE_CHEF', 'EN_REVUE_DA']).count(),
            'valides': queryset.filter(statut='VALIDE').count(),
            'rejetes': queryset.filter(statut__in=['REJETE_CHEF', 'REJETE_DA', 'REJETE_DEFINITIF']).count(),
            'plagiat_detecte': queryset.filter(est_plagiat=True).count(),
            'score_moyen_plagiat': queryset.filter(score_plagiat_global__gt=0).aggregate(
                avg_score=models.Avg('score_plagiat_global')
            )['avg_score'] or 0
        }
        
        return Response(stats)
