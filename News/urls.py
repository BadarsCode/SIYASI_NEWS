# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.home, name='home'),
#     path('article/<int:pk>/', views.article_detail, name='article_detail'),
# ]



from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.Home, name='home'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('gallery/', views.gallery, name='gallery'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('terms/', views.terms_view, name='terms'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),

    path('category/<str:category>/', views.category_view, name='category_view'),



    # API endpoints
    path('api/articles/', views.NewsArticleListAPI.as_view(), name='api_articles'),
    path('api/articles/<int:pk>/', views.NewsArticleDetailAPI.as_view(), name='api_article_detail'),
    path('category/<str:category_name>/', views.CategoryView, name='category'),
    # Chatbot
    path("chatbot/", views.chatbot_view, name="chatbot"),
    path("api/chatbot/", views.chatbot_api, name="chatbot_api"),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)