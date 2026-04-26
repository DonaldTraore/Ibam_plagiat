from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, LoginSerializer, UserProfileSerializer
)
from .models import UserProfile
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserListView(generics.ListAPIView):
    """
    Liste tous les utilisateurs.
    Accessible par les admins, chefs de département et DA.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.all()
        
        # Filtrer par rôle si spécifié
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
        
        # Filtrer par département si spécifié
        departement = self.request.query_params.get('departement', None)
        if departement:
            queryset = queryset.filter(departement=departement)
        
        # Filtrer par département pour les chefs de département
        if user.is_chef_departement:
            queryset = queryset.filter(departement=user.departement)
        
        return queryset.select_related('profile')


class UserDetailView(generics.RetrieveAPIView):
    """
    Détail d'un utilisateur.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'


class UserCreateView(generics.CreateAPIView):
    """
    Création d'un nouvel utilisateur.
    Accessible uniquement par les admins.
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        user = serializer.save()
        return user


class UserUpdateView(generics.UpdateAPIView):
    """
    Mise à jour d'un utilisateur.
    """
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'


class UserDeleteView(generics.DestroyAPIView):
    """
    Suppression d'un utilisateur.
    Accessible uniquement par les admins.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'


class CurrentUserView(APIView):
    """
    Retourne les informations de l'utilisateur connecté.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """
    Changement de mot de passe.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Vérifier l'ancien mot de passe
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {"old_password": ["Ancien mot de passe incorrect."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Changer le mot de passe
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response(
                {"message": "Mot de passe changé avec succès."},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileUpdateView(generics.UpdateAPIView):
    """
    Mise à jour du profil utilisateur.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.profile


class EtudiantListView(generics.ListAPIView):
    """
    Liste tous les étudiants.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(role='ETUDIANT')


class ChefDepartementListView(generics.ListAPIView):
    """
    Liste tous les chefs de département.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(role='CHEF_DEPARTEMENT')


class DAListView(generics.ListAPIView):
    """
    Liste tous les directeurs académiques.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(role='DA')


class SecretaireListView(generics.ListAPIView):
    """
    Liste tous les secrétaires.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(role='SECRETAIRE')
