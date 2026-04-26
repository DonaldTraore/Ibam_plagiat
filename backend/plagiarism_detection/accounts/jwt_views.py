"""
Views personnalisées pour JWT avec email
"""
from rest_framework_simplejwt.views import TokenObtainPairView
from .jwt_serializers import EmailTokenObtainPairSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    """
    Vue qui accepte email et password au lieu de username
    """
    serializer_class = EmailTokenObtainPairSerializer
