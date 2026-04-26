from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Modèle utilisateur personnalisé pour le système de détection de plagiat.
    """
    class Role(models.TextChoices):
        ETUDIANT = 'ETUDIANT', _('Étudiant')
        CHEF_DEPARTEMENT = 'CHEF_DEPARTEMENT', _('Chef de Département')
        DA = 'DA', _('Directeur Académique')
        SECRETAIRE = 'SECRETAIRE', _('Secrétaire')
        ADMIN = 'ADMIN', _('Administrateur')
    
    class Departement(models.TextChoices):
        INFORMATIQUE = 'INFORMATIQUE', _('Informatique')
        MATHEMATIQUES = 'MATHEMATIQUES', _('Mathématiques')
        PHYSIQUE = 'PHYSIQUE', _('Physique')
        CHIMIE = 'CHIMIE', _('Chimie')
        BIOLOGIE = 'BIOLOGIE', _('Biologie')
        DROIT = 'DROIT', _('Droit')
        ECONOMIE = 'ECONOMIE', _('Économie')
        MEDECINE = 'MEDECINE', _('Médecine')
        LETTRES = 'LETTRES', _('Lettres')
        AUTRE = 'AUTRE', _('Autre')

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    
    # Informations académiques
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.ETUDIANT,
        verbose_name=_('Rôle')
    )
    departement = models.CharField(
        max_length=20,
        choices=Departement.choices,
        default=Departement.AUTRE,
        verbose_name=_('Département')
    )
    matricule = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Matricule')
    )
    niveau_etude = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Niveau d\'étude')
    )
    
    # Champs Django requis
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def is_etudiant(self):
        return self.role == self.Role.ETUDIANT
    
    @property
    def is_chef_departement(self):
        return self.role == self.Role.CHEF_DEPARTEMENT
    
    @property
    def is_da(self):
        return self.role == self.Role.DA
    
    @property
    def is_secretaire(self):
        return self.role == self.Role.SECRETAIRE
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN


class UserProfile(models.Model):
    """
    Profil utilisateur avec informations supplémentaires.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Numéro de téléphone')
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Adresse')
    )
    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name=_('Photo de profil')
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Biographie')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Profil Utilisateur')
        verbose_name_plural = _('Profils Utilisateurs')

    def __str__(self):
        return f"Profil de {self.user.get_full_name()}"
