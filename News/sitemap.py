from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import NewsArticle  # use your article/news model

class ArticleSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return NewsArticle.objects.all()

    def lastmod(self, obj):
        return obj.updated_at  # or obj.date if you use date

    def location(self, obj):
        return reverse('article_detail', args=[obj.slug])
