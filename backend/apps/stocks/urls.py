# backend/apps/stocks/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Hisse senedi veri görünümleri
    path('', views.stock_list, name='stock_list'),
    path('<str:symbol>/', views.stock_detail, name='stock_detail'),
    path('<str:symbol>/historical/', views.historical_data, name='historical_data'),
    
    # Piyasa verileri
    path('market/movers/', views.market_movers, name='market_movers'),
    path('market/sectors/', views.sector_performance, name='sector_performance'),
    path('market/indices/', views.market_indices, name='market_indices'),
    
    # Teknik göstergeler
    path('<str:symbol>/indicators/', views.technical_indicators, name='technical_indicators'),
    path('<str:symbol>/indicators/<str:indicator>/', views.indicator_detail, name='indicator_detail'),
    
    # Temettü ve finansal veriler
    path('<str:symbol>/dividends/', views.dividends, name='dividends'),
    path('<str:symbol>/financials/', views.financial_data, name='financial_data'),
    
    # Kullanıcı izleme listesi
    path('watchlist/', views.user_watchlist, name='user_watchlist'),
    path('watchlist/add/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/', views.remove_from_watchlist, name='remove_from_watchlist'),
]
