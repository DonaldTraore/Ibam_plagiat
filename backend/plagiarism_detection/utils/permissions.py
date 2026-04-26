"""
Permissions personnalisées pour le système de détection de plagiat.
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission pour les administrateurs.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsChefDepartement(permissions.BasePermission):
    """
    Permission pour les chefs de département.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_chef_departement


class IsDA(permissions.BasePermission):
    """
    Permission pour les directeurs académiques (DA).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_da


class IsSecretaire(permissions.BasePermission):
    """
    Permission pour les secrétaires.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_secretaire


class IsEtudiant(permissions.BasePermission):
    """
    Permission pour les étudiants.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_etudiant


class IsChefOrDA(permissions.BasePermission):
    """
    Permission pour les chefs de département ou DA.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_chef_departement or request.user.is_da or request.user.is_admin
        )


class IsOwnerOrChefOrDA(permissions.BasePermission):
    """
    Permission pour le propriétaire, le chef de département ou le DA.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Propriétaire
        if hasattr(obj, 'etudiant') and obj.etudiant == user:
            return True
        
        if hasattr(obj, 'user') and obj.user == user:
            return True
        
        # Chef de département du même département
        if user.is_chef_departement:
            if hasattr(obj, 'departement'):
                return obj.departement == user.departement
        
        # DA ou Admin
        return user.is_da or user.is_admin


class ReadOnly(permissions.BasePermission):
    """
    Permission en lecture seule.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
