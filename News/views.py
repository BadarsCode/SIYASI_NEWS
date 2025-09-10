# from django.shortcuts import render

# # Create your views here.
# from django.shortcuts import render
# from .models import NewsArticle

# def home(request):
#     articles = NewsArticle.objects.all().order_by('-published_at')
#     return render(request, 'news/home.html', {'articles': articles})

# def article_detail(request, pk):
#     article = get_object_or_404(NewsArticle, pk=pk)

#     return render(request, 'news/article_detail.html', {'article': article})



from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import NewsArticle

def news_split_view(request):
    articles = NewsArticle.objects.order_by('-published_at')[:5]  # slider
    top_articles = NewsArticle.objects.order_by('-published_at')[:5]  # sidebar top
    all_articles = NewsArticle.objects.all().order_by('-published_at')
    return render(request, 'news/home.html', {
        'articles': articles,
        'top_articles': top_articles,
        'all_articles': all_articles
    })


# def article_detail_ajax(request, pk):
#     article = get_object_or_404(NewsArticle, pk=pk)
#     html = render(request, 'news/article_partial.html', {'article': article}).content.decode('utf-8')
#     return JsonResponse({'html': html})

def gallery(request):
    articles = NewsArticle.objects.exclude(images="").order_by('-published_at')
    return render(request, 'news/gallery.html', {'articles': articles})

# Static policy/info pages
def privacy_view(request): return render(request, 'news/privacy.html')
def terms_view(request): return render(request, 'news/terms.html')
def about_view(request): return render(request, 'news/about.html')
def contact_view(request): return render(request, 'news/contact.html')


from django.shortcuts import render, get_object_or_404
from .models import NewsArticle

def article_detail(request, pk):
    article = get_object_or_404(NewsArticle, pk=pk)
    articles = NewsArticle.objects.exclude(pk=pk).order_by('-published_at')[:10]  # show 10 related
    return render(request, 'news/article_detail.html', {
        'article': article,
        'articles': articles
    })


