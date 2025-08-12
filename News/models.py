from django.db import models

# Create your models here.
class NewsArticle(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    images = models.ImageField(upload_to='news_images/', blank=True,  null = True)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    