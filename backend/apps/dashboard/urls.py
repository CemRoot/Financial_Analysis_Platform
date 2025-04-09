# backend/apps/dashboard/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.dashboard_summary, name='dashboard_summary'),
    path('widgets/', views.dashboard_widgets, name='dashboard_widgets'),
    path('recent-activity/', views.recent_activity, name='recent_activity'),
    path('market-overview/', views.market_overview, name='market_overview'),
    path('user-favorites/', views.user_favorites, name='user_favorites'),
    path('customize/', views.customize_dashboard, name='customize_dashboard'),
]
