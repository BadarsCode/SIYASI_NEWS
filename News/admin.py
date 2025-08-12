from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import NewsArticle

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at')
    search_fields = ('title', 'content')
    list_filter = ('published_at',)
    ordering = ('-published_at',)
