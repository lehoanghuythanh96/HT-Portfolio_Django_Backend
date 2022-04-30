from django.conf.urls import url
from rest_framework_simplejwt.views import TokenVerifyView

from .refreshToken import CookieTokenRefreshView, CustomTokenVerifyView
from .views import CreateUserAPIView, authenticate_user, UserRetrieveUpdateAPIView, VerifyGoogleTokenId

urlpatterns = [
    url(r'^user/create/$', CreateUserAPIView.as_view()),
    url(r'^userlogin/$', authenticate_user),
    url(r'^update/$', UserRetrieveUpdateAPIView.as_view()),
    url(r'^token/refresh/$', CookieTokenRefreshView.as_view(), name='token_refresh'),
    url(r'^token/verify/$', CustomTokenVerifyView.as_view(), name='token_verify'),
    url(r'^google/tokenid/verify/$', VerifyGoogleTokenId.as_view(), name='gg_tokenId_verify'),
]