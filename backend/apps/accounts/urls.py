# backend/apps/accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'watchlists', views.WatchlistViewSet, basename='watchlist')
router.register(r'watchlist-items', views.WatchlistItemViewSet, basename='watchlist-item')
router.register(r'preferences', views.UserPreferenceViewSet, basename='user-preference')
router.register(r'activities', views.UserActivityViewSet, basename='user-activity')
router.register(r'stock-interactions', views.StockInteractionViewSet, basename='stock-interaction')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.register_user, name='register'),
    path('direct-login/', views.direct_login, name='direct-login'),
]