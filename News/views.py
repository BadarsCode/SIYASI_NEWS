from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import NewsArticle

def home(request):
    articles = NewsArticle.objects.all().order_by('-published_at')
    return render(request, 'news/home.html', {'articles': articles})
