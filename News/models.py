from django.db import models

# Create your models here.
class NewsArticle(models.Model):
    categories = [
        ('Politics', 'Politics'),
        ('Sports', 'Sports'),
        ('Technology', 'Technology'),
        ('Health', 'Health'),
        ('Entertainment', 'Entertainment'),
        ('Business', 'Business'),
        ('World', 'World'),
        ('Science', 'Science'),
        ('Travel', 'Travel'),
        ('Lifestyle', 'Lifestyle'),
        ('Education', 'Education'),
        ('Environment', 'Environment'),
        ('Opinion', 'Opinion'),
        ('Culture', 'Culture'),
        ('Food', 'Food'),
        ('Fashion', 'Fashion'),
        ('History', 'History'),
        ('Music', 'Music'),
        ('Art', 'Art'),
        ('Religion', 'Religion'),
        ('Other', 'Other'),
    ]
    title = models.CharField(max_length=200)
    content = models.TextField()
    images = models.ImageField(upload_to='news_images/', blank=True,  null = True)
    published_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, choices=categories, default='Other')


    def __str__(self):
        return self.title
    