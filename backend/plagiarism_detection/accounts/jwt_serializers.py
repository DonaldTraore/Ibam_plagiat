"""
Serializers pour JWT avec email
"""
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework import exceptions

User = get_user_model()


class EmailTokenObtainPairSerializer(serializers.Serializer):
    """Serializer qui accepte email/password et génère des tokens JWT valides"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Chercher l'utilisateur par email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                'Email ou mot de passe incorrect',
                code='authentication_failed'
            )

        # Vérifier le mot de passe
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

        # Créer les tokens
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
