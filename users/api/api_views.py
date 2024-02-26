from rest_framework import filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from users.api.serializers import UserSerializer, ChangePasswordSerializer, UserCreateSerializer
from users.models import User
from users.security import set_jwt_cookies, set_jwt_access_cookie, unset_jwt_cookies


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'username']
    ordering_fields = ['id']

    @action(methods=['get'], detail=False, url_path='me', url_name='me')
    def me(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='change-password', url_name='change-password')
    def change_password(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'پسورد با موفقیت تغییر کرد.'}, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action == 'change_password':
            return ChangePasswordSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        return self.serializer_class


class TokenObtainPairView(jwt_views.TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        set_jwt_cookies(response, access_token, refresh_token)
        return response


class TokenRefreshView(jwt_views.TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        access_token = response.data['access']
        set_jwt_access_cookie(response, access_token)
        return response


class TokenBlacklistView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(data={'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        unset_jwt_cookies(response)
        return response
