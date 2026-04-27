"""
Views pour JWT
"""
from rest_framework_simplejwt.views import TokenObtainPairView
from .jwt_serializers import EmailTokenObtainPairSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    """Vue JWT standard"""
    serializer_class = EmailTokenObtainPairSerializer
