"""
Serializers personnalisés pour SimpleJWT avec email au lieu de username
"""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework import exceptions

User = get_user_model()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer qui accepte email et password au lieu de username
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Changer le champ username en email dans le serializer
        self.fields['email'] = self.fields.pop('username')

    def validate(self, attrs):
        # Récupérer l'email et le mot de passe
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise exceptions.AuthenticationFailed(
                'Email et mot de passe requis',
                code='authentication_failed'
            )

        # Chercher l'utilisateur par email et vérifier le mot de passe
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                'Email ou mot de passe incorrect',
                code='authentication_failed'
            )

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed(
                'Email ou mot de passe incorrect',
                code='authentication_failed'
            )

        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                'Compte désactivé',
                code='user_inactive'
            )

        # Créer les tokens manuellement
        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return data
