from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import NewsArticle

def home(request):
    articles = NewsArticle.objects.all().order_by('-published_at')
    return render(request, 'news/home.html', {'articles': articles})

def article_detail(request, pk):
    article = get_object_or_404(NewsArticle, pk=pk)
    return render(request, 'news/article_detail.html', {'article': article})
