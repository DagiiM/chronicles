
from django.contrib import admin
from django.urls import path,include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/', admin.site.urls),
    path('',include('client.urls')),
    path('',include('authentication.urls')),
    path('api/', include('notifications.urls')),
    path('api/',include('clinics.urls')),
    path('api/',include('pharmacy.urls')),
    path('api/',include('consultations.urls'))
]
