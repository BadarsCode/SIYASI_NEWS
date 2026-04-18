from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, reverse_lazy
from django.views.generic import TemplateView

from News.sitemap import ArticleSitemap
from . import views


sitemaps = {
    'articles': ArticleSitemap,
}

urlpatterns = [
    path('', views.Home, name='home'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('article/<int:pk>/save/', views.toggle_save_article, name='toggle_save_article'),
    path('gallery/', views.gallery, name='gallery'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('terms/', views.terms_view, name='terms'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('category/<str:category>/', views.category_view, name='category_view'),
    path('profile/', views.profile_view, name='profile'),
    path('api/articles/', views.NewsArticleListAPI.as_view(), name='api_articles'),
    path('api/articles/<int:pk>/', views.NewsArticleDetailAPI.as_view(), name='api_article_detail'),
    path('chat/', views.chat_page, name='chat_page'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/', include('allauth.urls')),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    path(
        'password-reset/confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('search/', views.search, name='search'),
]
