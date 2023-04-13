from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from authentication.views import EmailAuthToken
from .views import SearchView
from rest_framework.authtoken.views import obtain_auth_token
from .views import GetUserIDView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/',obtain_auth_token),
    path('api-login/', EmailAuthToken.as_view(), name='api_login'),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    path('search/', SearchView.as_view(), name='search'),
    path('get-user-id/', GetUserIDView.as_view(), name='get_user_id'),
    path('users/reset_password_confirm/<str:uidb64>/<str:token>/', UserViewSet.as_view({'post': 'password_reset_confirm'}), name='password_reset_confirm'),
]
