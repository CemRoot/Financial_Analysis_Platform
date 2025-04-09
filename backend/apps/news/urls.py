# backend/apps/news/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Haber listeleme ve detay görünümleri
    path('', views.news_list, name='news_list'),
    path('<int:news_id>/', views.news_detail, name='news_detail'),
    
    # Haber kategorileri
    path('categories/', views.news_categories, name='news_categories'),
    path('categories/<str:category>/', views.category_news, name='category_news'),
    
    # Hisse senedine özgü haberler
    path('stocks/<str:symbol>/', views.stock_news, name='stock_news'),
    
    # Duygu analizi
    path('sentiment-analysis/', views.sentiment_analysis, name='sentiment_analysis'),
    path('sentiment-trends/', views.sentiment_trends, name='sentiment_trends'),
    
    # Haber araması
    path('search/', views.search_news, name='search_news'),
    
    # Kullanıcı tercihleri
    path('preferences/', views.news_preferences, name='news_preferences'),
]
