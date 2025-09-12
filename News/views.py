from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import NewsArticle
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from rest_framework import generics
from .serializers import NewsArticleSerializer



class NewsArticleListAPI(generics.ListCreateAPIView):
    queryset = NewsArticle.objects.all().order_by('-published_at')
    serializer_class = NewsArticleSerializer

class NewsArticleDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer


def news_split_view(request):
    articles = NewsArticle.objects.order_by('-published_at')[:5]  # slider
    top_articles = NewsArticle.objects.order_by('-published_at')[:5]  # sidebar top
    all_articles = NewsArticle.objects.all().order_by('-published_at')
    return render(request, 'news/home.html', {
        'articles': articles,
        'top_articles': top_articles,
        'all_articles': all_articles
    })

def gallery(request):
    articles = NewsArticle.objects.exclude(images="").order_by('-published_at')
    return render(request, 'news/gallery.html', {'articles': articles})

# Static policy/info pages
def privacy_view(request): return render(request, 'news/privacy.html')
def terms_view(request): return render(request, 'news/terms.html')
def about_view(request): return render(request, 'news/about.html')
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        full_message = f"From: {name} < {email} >\n\n{message}"
        try:
            send_mail(
                subject="Contact Form Submission",
                message=full_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,

            )
            messages.success(request, "your message has been sent successfully!")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
        return redirect('contact')
    return render(request, 'news/contact.html')


from django.shortcuts import render, get_object_or_404
from .models import NewsArticle

def article_detail(request, pk):
    article = get_object_or_404(NewsArticle, pk=pk)
    articles = NewsArticle.objects.exclude(pk=pk).order_by('-published_at')[:10]  # show 10 related
    return render(request, 'news/article_detail.html', {
        'article': article,
        'articles': articles
    })


def CategoryView(request, category_name):
    articles = NewsArticle.objects.filter(category=category_name).order_by('-published_at')
    for i in articles:
        print(i)
    return render(request, 'news/category.html',  {'article': articles, 'category_name': category_name})
