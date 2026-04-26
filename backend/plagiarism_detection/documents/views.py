from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import ReferenceDocument
from .serializers import (
    ReferenceDocumentListSerializer, ReferenceDocumentDetailSerializer,
    ReferenceDocumentCreateSerializer, ReferenceDocumentUpdateSerializer
)
from ..utils.file_processor import FileProcessor


class ReferenceDocumentListView(generics.ListAPIView):
    """
    Liste tous les documents de référence avec filtrage.
    Accessible par tous les utilisateurs authentifiés.
    """
    queryset = ReferenceDocument.objects.filter(est_actif=True)
    serializer_class = ReferenceDocumentListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type_document', 'departement', 'annee', 'est_actif']
    search_fields = ['titre', 'auteur', 'description', 'mots_cles']
    ordering_fields = ['date_ajout', 'annee', 'titre']
    ordering = ['-date_ajout']
    
    def get_queryset(self):
        user = self.request.user
        queryset = ReferenceDocument.objects.filter(est_actif=True)
        
        # Filtrer par département pour les chefs de département
        if user.is_chef_departement:
            queryset = queryset.filter(departement=user.departement)
        
        return queryset.select_related('ajoute_par')


class ReferenceDocumentDetailView(generics.RetrieveAPIView):
    """
    Détail d'un document de référence.
    """
    queryset = ReferenceDocument.objects.all()
    serializer_class = ReferenceDocumentDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = ReferenceDocument.objects.all()
        
        if user.is_chef_departement:
            queryset = queryset.filter(departement=user.departement)
        
        return queryset.select_related('ajoute_par')


class ReferenceDocumentCreateView(generics.CreateAPIView):
    """
    Création d'un nouveau document de référence.
    Accessible par la secrétaire, les chefs de département et les DA.
    """
    queryset = ReferenceDocument.objects.all()
    serializer_class = ReferenceDocumentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def perform_create(self, serializer):
        user = self.request.user
        fichier = self.request.FILES.get('fichier')
        
        # Extraire le nom original du fichier
        fichier_nom_original = fichier.name if fichier else None
        
        # Créer le document
        document = serializer.save(
            ajoute_par=user,
            fichier_nom_original=fichier_nom_original
        )
        
        # Extraire le contenu du fichier
        try:
            processor = FileProcessor()
            result = processor.process_file(document.fichier.path)
            
            document.contenu_extrait = result['content']
            document.nombre_mots = result['word_count']
            document.nombre_pages = result.get('page_count', 0)
            document.save()
        except Exception as e:
            # Log l'erreur mais ne pas bloquer la création
            print(f"Erreur lors de l'extraction du contenu: {e}")
        
        return document


class ReferenceDocumentUpdateView(generics.UpdateAPIView):
    """
    Mise à jour d'un document de référence.
    """
    queryset = ReferenceDocument.objects.all()
    serializer_class = ReferenceDocumentUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = ReferenceDocument.objects.all()
        
        # Seuls la secrétaire, les chefs de département et les DA peuvent modifier
        if not (user.is_secretaire or user.is_chef_departement or user.is_da or user.is_admin):
            return ReferenceDocument.objects.none()
        
        if user.is_chef_departement:
            queryset = queryset.filter(departement=user.departement)
        
        return queryset


class ReferenceDocumentDeleteView(generics.DestroyAPIView):
    """
    Suppression d'un document de référence.
    """
    queryset = ReferenceDocument.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = ReferenceDocument.objects.all()
        
        if not (user.is_secretaire or user.is_chef_departement or user.is_da or user.is_admin):
            return ReferenceDocument.objects.none()
        
        if user.is_chef_departement:
            queryset = queryset.filter(departement=user.departement)
        
        return queryset


class ReferenceDocumentStatisticsView(APIView):
    """
    Statistiques sur les documents de référence.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        queryset = ReferenceDocument.objects.filter(est_actif=True)
        
        if user.is_chef_departement:
            queryset = queryset.filter(departement=user.departement)
        
        stats = {
            'total': queryset.count(),
            'total_mots': sum(doc.nombre_mots or 0 for doc in queryset),
            'par_type': {
                type_doc: queryset.filter(type_document=type_doc).count()
                for type_doc, _ in ReferenceDocument.TypeDocument.choices
            },
            'par_departement': {
                dept: queryset.filter(departement=dept).count()
                for dept, _ in User.Departement.choices
            } if user.is_da or user.is_admin else None
        }
        
        return Response(stats)
