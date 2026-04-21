from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from tinymce.models import HTMLField

class NewsArticle(models.Model):
    categories = [
        ("Politics", "Politics"),
        ("Sports", "Sports"),
        ("Technology", "Technology"),
        ("Health", "Health"),
        ("Entertainment", "Entertainment"),
        ("Business", "Business"),
        ("World", "World"),
        ("Science", "Science"),
        ("Travel", "Travel"),
        ("Lifestyle", "Lifestyle"),
        ("Education", "Education"),
        ("Environment", "Environment"),
        ("Opinion", "Opinion"),
        ("Culture", "Culture"),
        ("Food", "Food"),
        ("Fashion", "Fashion"),
        ("History", "History"),
        ("Music", "Music"),
        ("Art", "Art"),
        ("Religion", "Religion"),
        ("Other", "Other"),
    ]
    title = models.CharField(max_length=200)
    content = HTMLField()
    images = models.ImageField(upload_to="news_images/", blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, choices=categories, default="Other")

    def __str__(self):
        return self.title


class SavedArticle(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_articles")
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name="saved_by")
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article")
        ordering = ["-saved_at"]

    def __str__(self):
        return f"{self.user} saved {self.article}"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    location = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Profile for {self.user}"


UserModel = get_user_model()


@receiver(post_save, sender=UserModel)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)
