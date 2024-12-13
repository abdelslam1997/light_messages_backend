from rest_framework.generics import (
    CreateAPIView, 
    RetrieveAPIView,
    ListAPIView
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import get_user_model
from django.db.models import Q

from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer,
    UserSearchSerializer,
)
from .paginations import UserSearchPagination


User = get_user_model()

class UserRegistrationView(CreateAPIView, ListAPIView):
    ''' Handle new user registration '''
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserRetrieveView(RetrieveAPIView):
    ''' Retrieve the current user '''
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserSearchView(ListAPIView):
    ''' Search for users through their email '''
    permission_classes = [IsAuthenticated]
    serializer_class = UserSearchSerializer
    pagination_class = UserSearchPagination

    def get_queryset(self):
        query = self.request.GET.get('query')
        # At least 3 characters are required to search
        if not query or len(query) < 3:
            return User.objects.none()
        # Eliminate the users that are already in conversation with the current user
        return User.objects.exclude(
            Q(sender__receiver=self.request.user) | 
            Q(receiver__sender=self.request.user)
        ).filter(
            Q(email__icontains=query)
        ).exclude(id=self.request.user.id)
        
    
    def list(self, request, *args, **kwargs):
        queryset = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)